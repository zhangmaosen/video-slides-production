# Video Slides Production - 视频幻灯片生产技能

## Rex 交互规则

### 新建项目流程

用户说“新建视频项目”或“开始新项目”时，逐步引导：

1. **项目名称** → 生成目录名（如 `projects/tesla-semi-20260404`）
2. **报告文档** → 仓颉整理为 `slides_content.json`
3. **视觉风格** → 写入 `project_config.json`
4. **参考图** → 保存到 `assets/` + 生成 `ref_meta.json`
5. **确认配置** → 展示摘要，等用户确认

### 启动 Autoresearch Loop

用户说“开始生成图片”或“跑 autoresearch”时：

1. 确认当前项目（如果有多个项目，询问用户）
2. 确认 slides 范围（默认全部，或用户指定）
3. 确认迭代次数（默认 4）
4. 组装并执行命令：

```bash
SKILL_DIR="/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production"
cd "$SKILL_DIR" && nohup bash scripts/core/autoresearch.sh \
  --project projects/<项目目录名> \
  --slides "<slide编号列表>" \
  --iterations <次数> \
  > /tmp/autoresearch.log 2>&1 &
```

5. 回复用户：“已启动，Telegram 会收到每轮进度”

### 查看进度

用户问“进度如何”时：`tail -20 /tmp/autoresearch.log`

### 重跑指定 slide

用户说“重跑 slide 3”时：
- 清理该 slide 的旧文件
- 只跑指定的 slide：`--slides "3"`

---

## 概述

将报告/逐字稿转化为视频幻灯片的完整 Pipeline：

```
报告 → 逐字稿 → slides_content.json → 图片生成(Autoresearch) → TTS → 视频合成
```

---

## 快速开始

### 1. 新建项目

```bash
mkdir -p projects/my-project/{assets,prompts,slides}
```

创建 `project_config.json`：
```json
{
  "name": "项目名称",
  "style": "手绘漫画，混子说风格",
  "resolution": "1664x928",
  "slides_count": 12
}
```

准备 `slides_content.json`（逐字稿）和 `assets/`（参考图 + ref_meta.json）。

### 2. 运行 Autoresearch Loop

```bash
bash scripts/core/autoresearch.sh \
  --project projects/my-project \
  --slides "0 1 2 3 4" \
  --iterations 4
```

### 3. 查看结果

每轮迭代会推送到 Telegram：图片 + 评分详情。
跑完后推送汇总报告 + 询问是否启动 TTS。

---

## 核心流程

| 阶段 | 工具 | 说明 |
|------|------|------|
| a. 逐字稿整理 | 仓颉 | 报告 → slides_content.json |
| b. 素材准备 | 手动 | 参考图 + ref_meta.json |
| **c. 图片生成** | **autoresearch.sh** | **两层循环 × 4轮迭代** |
| d. TTS 语音 | ComfyUI Qwen-TTS | 茂森语音 Clone |
| e. 视频合成 | FFmpeg | 音画同步 + 字幕 |

---

## Autoresearch Loop

**驱动脚本：** `scripts/core/autoresearch.sh`

### 架构

```
bash 两层循环（程序层控制，不靠 LLM 记忆）
├── 外层：遍历 slides (0, 1, 2, ...)
│   └── 内层：每个 slide 迭代 N 次
│       ├── 1. 女娲生成/优化 prompt（openclaw agent 持久 session）
│       ├── 2. 哪吒生成图片（gen_slide.py → ComfyUI API）
│       ├── 3. 二郎神评分（同一 session，上下文累积）
│       └── 4. ≥90 提前退出 / 记录最高分
└── 跑完：推送汇总 → 驱动下一步
```

### 关键设计

- **持久 session**：每个 slide 独立 `--session-id`，女娲记得之前所有 prompt 和评分
- **循环在 bash 层**：不依赖 LLM 记忆循环计数
- **自动回退**：低分版本不影响下一轮（基于最高分版本优化）
- **Telegram 推送**：每轮图片+评分详情、新最高分、slide 完成、最终汇总

### 参数

```bash
bash scripts/core/autoresearch.sh \
  --project projects/[项目名] \     # 项目目录（相对 skill 根）
  --slides "0 1 2 3 4" \           # slide 编号
  --iterations 4 \                  # 每页迭代次数（默认 4）
  --no-lightning                    # 关闭 Lightning（默认开启）
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COMFYUI_API` | `http://100.111.221.7:8188` | ComfyUI 地址 |
| `NOTIFY_CHANNEL` | `telegram` | 通知频道 |

### Prompt 模板

三个模板在 `scripts/core/templates/`，修改 prompt 只需编辑 `.txt` 文件：

| 文件 | 用途 | 变量 |
|------|------|------|
| `init.txt` | 女娲首次生成 prompt | `${SLIDE_FMT}`, `${PROJECT_STYLE}`, `${PROJECT_DIR}` |
| `score.txt` | 二郎神评分 | `${ITER}`, `${ITERATIONS}`, `${IMG_FILE}` |
| `optimize.txt` | 女娲优化 prompt | `${NEXT}`, `${BEST_VERSION}`, `${SCORE_FEEDBACK}` |

变量通过 `envsubst` 自动替换。

---

## 团队角色

| 角色 | 职责 | System Prompt | 使用方式 |
|------|------|---------------|----------|
| **仓颉** | 报告 → 逐字稿 | `SYSTEM_PROMPT_CANGJIE.md` | Rex spawn |
| **女娲** | 生成/优化 prompt | `SYSTEM_PROMPT_NVWA.md` | autoresearch.sh 内 |
| **哪吒** | 生成图片 | - | gen_slide.py |
| **二郎神** | 评分图片 | `SYSTEM_PROMPT_ERLANG.md` | autoresearch.sh 内 |

---

## 评分标准（二郎神）

详见 `SYSTEM_PROMPT_ERLANG.md`

| 维度 | 分值 | 子项 |
|------|------|------|
| 文字准确性 | 30分 | 主标题(10) + 副标题/数据(10) + 清晰度(10) |
| 场景内容 | 40分 | 有参考图：造型+特征+细节+比例；无参考图：场景+叙事+细节 |
| 整体表现 | 30分 | 视觉冲击力(10) + 风格一致性(10) + AI瑕疵(10) |

---

## 项目结构

```
video-slides-production/
├── SKILL.md                          # 本文档
├── SYSTEM_PROMPT_NVWA.md             # 女娲 System Prompt (v5.0)
├── SYSTEM_PROMPT_CANGJIE.md          # 仓颉 System Prompt
├── SYSTEM_PROMPT_ERLANG.md           # 二郎神 System Prompt (v8.0)
├── ComfyUI/
│   └── Qwen-Image-2512_ComfyUI.json # ComfyUI 工作流
├── scripts/
│   └── core/
│       ├── autoresearch.sh           # 主驱动脚本（两层循环）
│       ├── gen_slide.py              # ComfyUI 单张生图
│       └── templates/
│           ├── init.txt              # 女娲初始化模板
│           ├── score.txt             # 二郎神评分模板
│           └── optimize.txt          # 女娲优化模板
└── projects/
    └── [项目名]/
        ├── project_config.json       # 项目配置（风格、分辨率等）
        ├── slides_content.json       # 逐字稿内容
        ├── prompts/slide_XX/         # 每页的 prompt 版本
        ├── slides/                   # 生成的图片
        └── assets/                   # 参考图 + ref_meta.json
```

### project_config.json

```json
{
  "name": "项目名称",
  "style": "手绘漫画，混子说风格",
  "resolution": "1664x928",
  "slides_count": 12,
  "has_maosen_ip": true,
  "has_maosen_voice": true,
  "reference_images": ["assets/ref_01.jpg", "assets/ref_02.jpg"]
}
```

### ref_meta.json

```json
{
  "ref_01_exterior.jpg": {
    "用途": "参考外观特征（车身、车灯、比例）",
    "忽略": "纯白棚拍背景"
  }
}
```

---

## 单张生图

```bash
python3 scripts/core/gen_slide.py \
  --project projects/[项目名] \
  --slide 00 \
  --version 1 \
  --lightning
```

默认 Lightning 模式（4 steps，快 10 倍）。去掉 `--lightning` 用标准模式（50 steps）。

---

**版本**：v11.0 (2026-04-04)
