# Video Slides Production - 视频幻灯片生产技能

## 核心流程

```
a. 逐字稿 → slides_content.md（观点|逐字稿|背景知识）
b. 素材整理（图片、茂森IP）
c. 图片生成（女娲一页一页生成提示词）
   c1. 女娲生成提示词（System Prompt + 用户输入）
   c2. ComfyUI 生成图片
   c3. 二郎神评分 + 哪吒优化（循环直到 92 分）
d. TTS生成（茂森语音 Clone）
e. FFmpeg 视频合成
```

---

## a. 逐字稿格式化

### 输入格式
```
标题：xxx
00|第一页观点
01|第二页观点
...
```

### 输出格式（slides_content.md）
```
### 编号 | 标题
- **观点**：xxx
- **逐字稿**：xxx
- **背景知识**：xxx（必要时用浏览器搜索获取）
```

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

女娲使用固定 System Prompt + 用户输入，自动分类处理生成提示词。

**System Prompt 文件：** `SYSTEM_PROMPT.md`

**用户输入格式：**
```
标题：xxx
观点：xxx
逐字稿：xxx
背景知识：xxx
```

**关键步骤 - 读取素材图片：**
女娲在生成每个提示词前，必须使用 image 工具读取对应的素材图片，提取视觉特征。

### c2. 评分迭代流程

```
ComfyUI 生成图片
    ↓
二郎神评分（详细扣分汇报）
    ↓
哪吒优化提示词（如 < 92 分）
    ↓
重新生成图片
    ↓
重复直到 >= 92 分
```

**二郎神职责：**
- 读取参考图片和待评分图片
- 逐项对比，详细汇报扣分点
- 记录所有问题到负向提示词

**哪吒职责：**
- 根据二郎神反馈优化提示词
- 将被扣分的点加入负向提示词
- 生成优化后的图片

**通过标准：92 分+**

### c3. 图片生成脚本

**通用脚本：** `scripts/core/batch_generate_images.py`

**使用方式：**
```bash
cd /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production
python3 scripts/core/batch_generate_images.py \
  --project projects/semi-ev3_20260403 \
  --prompt-file prompts/slide_01.txt \
  --output projects/semi-ev3_20260403/slides/slide_01.png \
  --seed random
```

---

## d. TTS生成（茂森语音 Clone）

### 正确工作流（必须遵守）
```
VoiceDesign（节点 3）→ VoiceClone（节点 40）→ 目标音频
```

### Rex 角色设定
- 姓名：Rex
- 音色：低沉浑厚，自然停顿，节奏感强
- instruct：详见 `skills/qwen-tts/SKILL.md`

---

## e. FFmpeg 视频合成

### 字幕叠加
- 必须加 `format=rgba` 才能使用 PNG alpha 通道
- macOS 中文字体：`/System/Library/Fonts/STHeiti Medium.ttc`

### 音视频同步
- 视频片段必须基于实际音频时长生成
- 音频 concat 统一转为 AAC 再合并

---

## 项目结构

```
video-slides-production/
├── SKILL.md                    # 本文档
├── SCORING.md                  # 评分标准
├── SYSTEM_PROMPT.md            # 女娲 System Prompt
├── ComfyUI/                   # ComfyUI 工作流
├── scripts/                   # 通用脚本
│   └── core/                  # 核心脚本
│       └── batch_generate_images.py
└── projects/                  # 项目目录
    └── semi-ev3_20260403/
        ├── slides_content.md   # 幻灯片内容
        ├── prompts/           # 提示词文件
        ├── slides/            # 生成的图片
        └── assets/            # 素材图片
```

---

## 常用命令

### 生成图片
```bash
cd /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production
python3 scripts/core/batch_generate_images.py \
  --project projects/semi-ev3_20260403 \
  --prompt-file prompts/slide_01.txt \
  --output projects/semi-ev3_20260403/slides/slide_01.png
```

### 检查 ComfyUI 状态
```bash
curl http://100.111.221.7:8188/system_stats
```

---

**版本**：v3.0 (2026-04-04)
**更新**：简化女娲流程，移除 META_PROMPT，改为 System Prompt 直接注入
