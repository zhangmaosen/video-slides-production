#!/bin/bash
#
# Autoresearch Loop 驱动脚本
# 两层循环：slide 页数 × 每页迭代次数
# 使用 openclaw agent --session-id 持久 session 累积上下文
#
# 用法：
#   bash scripts/core/autoresearch.sh --project projects/tesla-semi-20260404 --slides "0 1" --iterations 4
#   bash scripts/core/autoresearch.sh --project projects/tesla-semi-20260404 --slides "0 1 2 3 4 5 6 7 8 9 10 11" --iterations 4
#

set -euo pipefail

# ============================================================
# 参数解析
# ============================================================

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT=""
SLIDES=""
ITERATIONS=4
LIGHTNING="--lightning"

while [[ $# -gt 0 ]]; do
  case $1 in
    --project) PROJECT="$2"; shift 2 ;;
    --slides) SLIDES="$2"; shift 2 ;;
    --iterations) ITERATIONS="$2"; shift 2 ;;
    --no-lightning) LIGHTNING=""; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$PROJECT" ] || [ -z "$SLIDES" ]; then
  echo "Usage: bash autoresearch.sh --project <project_dir> --slides \"0 1 2\" [--iterations 4] [--no-lightning]"
  exit 1
fi

PROJECT_DIR="${SKILL_DIR}/${PROJECT}"
CONFIG_FILE="${PROJECT_DIR}/project_config.json"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 项目目录不存在: $PROJECT_DIR"
  exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 配置文件不存在: $CONFIG_FILE"
  exit 1
fi

PROJECT_NAME=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['name'])")
PROJECT_STYLE=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['style'])")
PROJECT_RESOLUTION=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['resolution'])")
RES_WIDTH=$(echo "$PROJECT_RESOLUTION" | cut -d'x' -f1)
RES_HEIGHT=$(echo "$PROJECT_RESOLUTION" | cut -d'x' -f2)
SLIDES_TOTAL=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['slides_count'])")
COMFYUI_API="${COMFYUI_API:-http://100.111.221.7:8188}"
NOTIFY_CHANNEL="${NOTIFY_CHANNEL:-telegram}"
GEN_SCRIPT="${SKILL_DIR}/scripts/core/gen_slide.py"
TEMPLATE_DIR="${SKILL_DIR}/scripts/core/templates"
TIMEOUT=180

echo ""
echo "========================================================"
echo "  Autoresearch Loop"
echo "  项目: ${PROJECT_NAME} (${PROJECT_STYLE})"
echo "  Slides: ${SLIDES}"
echo "  每页迭代: ${ITERATIONS} 次"
echo "  Lightning: $([ -n "$LIGHTNING" ] && echo '是' || echo '否')"
echo "========================================================"

# ============================================================
# ComfyUI 状态检查
# ============================================================

echo ""
echo "[检查 ComfyUI...]"
STATS=$(curl -s "${COMFYUI_API}/system_stats" 2>/dev/null || echo "")
if [ -z "$STATS" ]; then
  echo "❌ ComfyUI 不可达: ${COMFYUI_API}"
  exit 1
fi
echo "  ✓ ComfyUI 在线"

# ============================================================
# 辅助函数
# ============================================================

# 调用 openclaw agent（持久 session）
call_agent() {
  local SESSION_ID="$1"
  local MESSAGE="$2"
  local AGENT_TIMEOUT="${3:-$TIMEOUT}"
  
  openclaw agent \
    --session-id "$SESSION_ID" \
    --json \
    --message "$MESSAGE" \
    --timeout "$AGENT_TIMEOUT" 2>/dev/null
}

# 从 agent JSON 输出中提取文本
extract_text() {
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    payloads = data.get('result', {}).get('payloads', [])
    if payloads:
        print(payloads[0].get('text', ''))
    else:
        print(json.dumps(data)[:500])
except:
    print(sys.stdin.read()[:500])
"
}

# 从文本中提取分数
extract_score() {
  python3 -c "
import sys, re
text = sys.stdin.read()
for pat in [r'(?:total|总分)[^0-9]*(\d+)', r'(\d+)\s*/\s*100']:
    m = re.search(pat, text, re.IGNORECASE)
    if m:
        print(m.group(1))
        sys.exit(0)
print('0')
"
}

# 发送通知到 Telegram（关键节点推送）
notify() {
  local MSG="$1"
  local IMG="${2:-}"
  if [ -n "$IMG" ] && [ -f "$IMG" ]; then
    # 发送图片+文字
    openclaw agent \
      --session-id "notify-autoresearch" \
      --message "请发送图片 ${IMG} 给用户，附带消息：${MSG}" \
      --deliver --channel "$NOTIFY_CHANNEL" \
      --timeout 30 >/dev/null 2>&1 &
  else
    openclaw agent \
      --session-id "notify-autoresearch" \
      --message "$MSG" \
      --deliver --channel "$NOTIFY_CHANNEL" \
      --timeout 15 >/dev/null 2>&1 &
  fi
}

# 渲染模板（用 envsubst 替换变量）
render_template() {
  local TEMPLATE_FILE="${TEMPLATE_DIR}/$1"
  if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ 模板文件不存在: $TEMPLATE_FILE" >&2
    return 1
  fi
  envsubst < "$TEMPLATE_FILE"
}

# ============================================================
# 外层循环：遍历 slides
# ============================================================

for SLIDE_NUM in $SLIDES; do
  SLIDE_FMT=$(printf "%02d" "$SLIDE_NUM")

  echo ""
  echo "========================================================"
  echo "  开始 slide_${SLIDE_FMT}"
  echo "========================================================"

  # 创建目录
  PROMPT_DIR="${PROJECT_DIR}/prompts/slide_${SLIDE_FMT}"
  mkdir -p "$PROMPT_DIR" "${PROJECT_DIR}/slides"

  # 为每个 slide 创建独立 session
  SESSION_ID="autor-${SLIDE_FMT}-$(date +%s)"
  
  BEST_VERSION=0
  BEST_SCORE=0

  # ==== 第 1 轮：初始化 session + 生成 v1 prompt ====
  echo ""
  echo "  [第 1/${ITERATIONS} 轮] 初始化 + 女娲 v1"
  
  export SLIDE_FMT ITERATIONS PROJECT_STYLE PROJECT_DIR PROMPT_DIR
  INIT_MSG=$(render_template "init.txt")

  REPLY=$(echo "$INIT_MSG" | xargs -0 openclaw agent --session-id "$SESSION_ID" --json --timeout "$TIMEOUT" --message 2>/dev/null | extract_text)
  echo "  女娲 v1: ${REPLY:0:100}..."

  # ==== 内层循环：迭代 ====
  for ITER in $(seq 1 $ITERATIONS); do
    ITER_FMT=$(printf "%d" "$ITER")
    
    echo ""
    echo "  ---- 第 ${ITER}/${ITERATIONS} 轮 ----"

    # 检查 prompt 文件是否存在
    POS_FILE="${PROMPT_DIR}/v${ITER}_positive.txt"
    NEG_FILE="${PROMPT_DIR}/v${ITER}_negative.txt"
    
    if [ ! -f "$POS_FILE" ]; then
      echo "  ⚠️ prompt 文件不存在: ${POS_FILE}，跳过"
      continue
    fi
    
    POS_LEN=$(wc -c < "$POS_FILE" | tr -d ' ')
    echo "  prompt: ${POS_LEN} 字符"

    # 哪吒：生成图片
    echo "  [哪吒] 生成图片..."
    python3 "$GEN_SCRIPT" \
      --project "$PROJECT" \
      --slide "$SLIDE_FMT" \
      --version "$ITER" \
      --width "$RES_WIDTH" --height "$RES_HEIGHT" \
      $LIGHTNING 2>&1 | while IFS= read -r line; do echo "    $line"; done
    
    IMG_FILE="${PROJECT_DIR}/slides/slide_${SLIDE_FMT}_v${ITER}.png"
    if [ ! -f "$IMG_FILE" ]; then
      echo "  ❌ 图片生成失败"
      continue
    fi
    IMG_SIZE=$(du -h "$IMG_FILE" | cut -f1)
    echo "  ✓ 图片: ${IMG_FILE} (${IMG_SIZE})"

    # 二郎神：评分
    echo "  [二郎神] 评分..."
    export ITER ITERATIONS IMG_FILE
    SCORE_MSG=$(render_template "score.txt")

    SCORE_REPLY=$(call_agent "$SESSION_ID" "$SCORE_MSG" "$TIMEOUT" | extract_text)
    SCORE=$(echo "$SCORE_REPLY" | extract_score)
    
    echo "  ★ v${ITER} = ${SCORE}/100"
    echo "  反馈: ${SCORE_REPLY:0:200}..."

    # 更新最高分
    if [ "$SCORE" -gt "$BEST_SCORE" ]; then
      BEST_SCORE=$SCORE
      BEST_VERSION=$ITER
      echo "  🏆 新最高分！v${ITER} = ${SCORE}"
      notify "🏆 slide_${SLIDE_FMT} v${ITER} = ${SCORE}/100 新最高分

${SCORE_REPLY:0:500}" "$IMG_FILE"
    else
      echo "  → 保持 v${BEST_VERSION} = ${BEST_SCORE}"
      notify "📊 slide_${SLIDE_FMT} v${ITER} = ${SCORE}/100（保持 v${BEST_VERSION}=${BEST_SCORE}）

${SCORE_REPLY:0:500}" "$IMG_FILE"
    fi

    # 记录 CHANGELOG
    echo "- v${ITER}: ${SCORE}分" >> "${PROMPT_DIR}/CHANGELOG.md"

    # >= 90 提前结束
    if [ "$SCORE" -ge 90 ]; then
      echo "  🎉 v${ITER} >= 90，提前结束！"
      notify "🎉 slide_${SLIDE_FMT} v${ITER} = ${SCORE}/100 >= 90 提前结束！"
      break
    fi

    # 下一轮：女娲优化
    if [ "$ITER" -lt "$ITERATIONS" ]; then
      NEXT=$((ITER + 1))
      echo "  [女娲] 生成 v${NEXT}..."
      
      export NEXT BEST_VERSION BEST_SCORE ITER ITERATIONS PROMPT_DIR
      export SCORE_FEEDBACK="${SCORE_REPLY:0:600}"
      OPTIM_MSG=$(render_template "optimize.txt")

      OPTIM_REPLY=$(call_agent "$SESSION_ID" "$OPTIM_MSG" "$TIMEOUT" | extract_text)
      echo "  女娲 v${NEXT}: ${OPTIM_REPLY:0:100}..."
    fi
  done

  # slide 完成
  echo ""
  echo "  ========================================"
  echo "  slide_${SLIDE_FMT} 完成！"
  echo "  最终: v${BEST_VERSION} = ${BEST_SCORE}分"
  echo "  ========================================"
  notify "✅ slide_${SLIDE_FMT} 完成！最终: v${BEST_VERSION} = ${BEST_SCORE}/100"
  
  # 写最终 CHANGELOG
  echo "" >> "${PROMPT_DIR}/CHANGELOG.md"
  echo "**最终选择: v${BEST_VERSION} = ${BEST_SCORE}分**" >> "${PROMPT_DIR}/CHANGELOG.md"

done

# ============================================================
# 最终汇报
# ============================================================

echo ""
echo "========================================================"
echo "  全部完成！"
echo "========================================================"

# 构建汇报消息
REPORT="✅ Autoresearch Loop 完成\n项目：${PROJECT_NAME}\n\n"
for SLIDE_NUM in $SLIDES; do
  SLIDE_FMT=$(printf "%02d" "$SLIDE_NUM")
  CL_FILE="${PROJECT_DIR}/prompts/slide_${SLIDE_FMT}/CHANGELOG.md"
  if [ -f "$CL_FILE" ]; then
    BEST_LINE=$(grep "最终选择" "$CL_FILE" 2>/dev/null || echo "未完成")
    REPORT+="slide_${SLIDE_FMT}: ${BEST_LINE}\n"
  fi
done

notify "$(echo -e "$REPORT")"
