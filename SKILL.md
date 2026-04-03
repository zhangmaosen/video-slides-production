# Video Slides Production - 视频幻灯片生产技能

## 核心流程

```
a. 逐字稿 → slides_content.json（内容整理 Agent）
b. 素材整理（图片、茂森IP）
c. 图片生成
   c1. 女娲生成 prompt
   c2. 哪吒调用 gen_slide.py
   c3. 二郎神评分（循环直到 92 分）
d. TTS生成
e. FFmpeg 视频合成
```

---

## a. 逐字稿格式化

### Step 1: 生成 slides_content.json

**输入：** `script.md`（Markdown 表格）
**输出：** `slides_content.json`

**Agent System Prompt：** `SYSTEM_PROMPT_CONTENT.md`

**流程：**
1. 读取 `SYSTEM_PROMPT_CONTENT.md`
2. 读取 `script.md`
3. Agent 生成 JSON

---

## b. 素材整理

### 茂森 IP 形象描述
```
茂森：Q版，蓬松黑发，八字浓眉，白色T恤，自信表情，穿着休闲
```

### 茂森语音参考
- 文件：`tmp-slides/maosen_voice_sample.mp4`

---

## c. 图片生成

### c1. 女娲生成提示词

**读取文件：**
- `project_config.json` - style, resolution
- `slides_content.json` - 幻灯片内容
- `assets/` - 参考图

**Agent System Prompt：** `SYSTEM_PROMPT.md`

**流程：**
1. 女娲读取 `SYSTEM_PROMPT.md`
2. 读取 `project_config.json` 获取 style
3. 读取 `slides_content.json` 获取内容
4. 读取 `assets/` 中的参考图
5. 生成提示词 → `prompts/slide_XX/vN_*.txt`
6. 更新 `CHANGELOG.md`

### c2. 哪吒生成图片

**脚本：** `scripts/core/gen_slide.py`

```bash
python3 scripts/core/gen_slide.py \
  --project projects/semi-ev3_20260403 \
  --slide 00 \
  --version 1
```

**输出：** `slides/slide_00_v1.png`

### c3. 二郎神评分

```
评分标准（100分）：
- 标题准确性（一票否决）
- 标题内容：10分
- 故事性：25分
- 参考物神似度：30分
- 视觉吸引力：15分
- 风格一致性：10分
- 其它文字：10分

通过标准：92分+
```

**流程：**
1. 二郎神评分
2. 如 < 92 → 女娲优化 prompt → c2
3. 循环直到 >= 92

---

## d. TTS生成

### 正确工作流
```
VoiceDesign（节点 3）→ VoiceClone（节点 40）→ 目标音频
```

---

## e. FFmpeg 视频合成

### 字幕叠加
- 必须加 `format=rgba`
- macOS 中文字体：`/System/Library/Fonts/STHeiti Medium.ttc`

---

## 项目结构

```
video-slides-production/
├── SKILL.md                     # 本文档
├── SCORING.md                 # 评分标准
├── SYSTEM_PROMPT.md           # 女娲 System Prompt
├── SYSTEM_PROMPT_CONTENT.md    # 内容整理 System Prompt
├── ComfyUI/                  # ComfyUI 工作流
├── scripts/
│   └── core/
│       └── gen_slide.py      # 生成图片脚本
└── projects/
    └── semi-ev3_20260403/
        ├── project_config.json    # 项目配置
        ├── slides_content.json    # 幻灯片内容
        ├── script.md             # 原始逐字稿
        ├── prompts/              # 提示词（版本化）
        │   └── slide_00/
        │       ├── v1_positive.txt
        │       ├── v1_negative.txt
        │       └── CHANGELOG.md
        ├── slides/              # 生成的图片
        └── assets/              # 参考图
```

---

## 常用命令

### 检查 ComfyUI 状态
```bash
curl http://100.111.221.7:8188/system_stats
```

---

**版本**：v4.0 (2026-04-04)
**更新**：新增内容整理 Agent，完善流程文档
