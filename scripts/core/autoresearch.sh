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
  
  INIT_MSG="你现在负责为 slide_${SLIDE_FMT} 完成 ${ITERATIONS} 轮 Autoresearch Loop。

【核心规则 - 违反任何一条 = 废稿重来】
1. 风格：${PROJECT_STYLE}（非写实摄影）
2. 封面页(slide_00)用 main_title 和 subtitle 作为文字
3. 非封面页从 script/viewpoint 提取文字，禁止用封面标题
4. 非封面页必须画故事场景，不是车辆棚拍
5. ⚠️ prompt 总字符数 400-700，绝对不超过 800！超过 800 直接作废！

【开始】
1. 读取 ${PROJECT_DIR}/slides_content.json，找到 slide_${SLIDE_FMT} 的内容
2. 读取 ${PROJECT_DIR}/assets/ref_meta.json 了解参考图用途
3. 读取 ${PROJECT_DIR}/assets/ 目录下的参考图
4. 生成 v1 prompt，写入：
   - ${PROMPT_DIR}/v1_positive.txt
   - ${PROMPT_DIR}/v1_negative.txt
5. 回复确认 prompt 已写入文件 + 字符数"

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
    SCORE_MSG="【第 ${ITER}/${ITERATIONS} 轮：二郎神评分】

请读取图片：${IMG_FILE}
然后严格评分（100分制）：
- 文字准确性：30分
- 参考对象准确性：40分（或故事表达能力30分）
- 故事表达能力：30分

回复格式：
总分: X/100
文字准确性：X/30
参考对象准确性：X/40（或故事表达 X/30）
故事表达能力：X/30
---
[问题]
1. ...
---
[优化建议]
1. ..."

    SCORE_REPLY=$(call_agent "$SESSION_ID" "$SCORE_MSG" "$TIMEOUT" | extract_text)
    SCORE=$(echo "$SCORE_REPLY" | extract_score)
    
    echo "  ★ v${ITER} = ${SCORE}/100"
    echo "  反馈: ${SCORE_REPLY:0:200}..."

    # 更新最高分
    if [ "$SCORE" -gt "$BEST_SCORE" ]; then
      BEST_SCORE=$SCORE
      BEST_VERSION=$ITER
      echo "  🏆 新最高分！v${ITER} = ${SCORE}"
      notify "🎨 slide_${SLIDE_FMT} v${ITER} = ${SCORE}/100 🏆 新最高分" "$IMG_FILE"
    else
      echo "  → 保持 v${BEST_VERSION} = ${BEST_SCORE}"
      notify "📊 slide_${SLIDE_FMT} v${ITER} = ${SCORE}/100（保持 v${BEST_VERSION}=${BEST_SCORE}）" "$IMG_FILE"
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
      
      OPTIM_MSG="【第 ${NEXT}/${ITERATIONS} 轮：女娲优化 prompt】

当前最高分：v${BEST_VERSION}=${BEST_SCORE}分

二郎神对 v${ITER} 的反馈：
${SCORE_REPLY:0:600}

请基于 v${BEST_VERSION} 的 prompt + 二郎神反馈，生成 v${NEXT} prompt。
读取 ${PROMPT_DIR}/v${BEST_VERSION}_positive.txt 作为基础。
写入：
- ${PROMPT_DIR}/v${NEXT}_positive.txt
- ${PROMPT_DIR}/v${NEXT}_negative.txt

回复确认 prompt 已写入 + 字符数 + 主要改动点"

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

echo ""
echo "========================================================"
echo "  全部完成！"
echo "========================================================"
