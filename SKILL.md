# Video Slides Production - 视频幻灯片生产技能

## 核心流程

```
a. 逐字稿 → slides_content.md（观点|逐字稿|背景知识）
b. 素材整理（图片、茂森IP）
c. 图片生成（女娲一页一页生成提示词）
   c1. 元提示词模板实例化
   c2. Agent 根据实例化模板生成 slide 提示词
   c3. ComfyUI 生成图片
   c4. 二郎神评分 + 哪吒优化（循环直到 92 分）
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

### c1. 元提示词模板实例化流程

**⚠️ 重要原则：女娲必须一页一页生成每张 slide 的初始提示词，保证质量**

#### 完整工作流程

```
1. 元提示词模板实例化
   ↓
2. Agent 根据实例化模板生成 slide 提示词
   ↓
3. ComfyUI 生成图片
   ↓
4. 二郎神评分
   ↓
5. 哪吒优化（如需）
   ↓
6. 重复 3-5 直到达到 92 分
   ↓
7. 下一张 slide...
```

#### Step 1: 元提示词模板实例化

女娲需要：
1. 读取项目元提示词模板（`projects/semi-ev3_20260403/META_PROMPT_PROJECT.md`）
2. 读取对应 slide 的逐字稿内容（从 `slides_content.md`）
3. 读取相关素材图片获取视觉特征（使用 image 工具）
4. 将内容插入模板的正确位置

**实例化输出格式：**
```
你是一个顶级的幻灯片视觉设计师...

请为以下 slide 生成提示词：

标题：xxx
观点：xxx
核心数据：xxx
背景知识：xxx

素材图片特征（从 xxx.png 提取）：
- xxx
- xxx

请严格按照元提示词模板规则生成提示词。
```

#### Step 2: Agent 生成 slide 提示词

女娲将实例化后的内容发送给 Agent，Agent 输出纯净的 slide 提示词。

#### Step 3-6: 图片生成 → 评分 → 优化循环

### c2. 项目元提示词模板

**模板文件：** `projects/semi-ev3_20260403/META_PROMPT_PROJECT.md`

**模板核心规则：**
1. **风格绝对统一**：提取 1-2 个核心风格词放句首
2. **精简文字提取**：只提炼标题/观点/核心数据，用英文双引号包裹
3. **主体最详尽**：详尽描写材质、颜色，光影、数量、动作
4. **空间关系明确**：明确左右/前后/上下层级，指出留白
5. **绝对正向描述**：不用负面词汇
6. **故事感核心**：冲突双方 + 动态动作 + 场景叙事 + 视觉张力 + 隐喻表达
7. **中文输出**：所有提示词必须使用中文（除必要的英文品牌/术语）
8. **纯净静默输出**：只输出 prompt 文本

**关键步骤 - 读取素材图片：**
女娲在生成每个提示词前，必须使用 image 工具读取对应的素材图片，提取视觉特征。

### c3. 评分迭代流程

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

### c4. 图片生成脚本

**通用脚本：** `scripts/core/batch_generate_images.py`

**使用方式：**
```bash
cd skills/video-slides-production
python3 scripts/core/batch_generate_images.py \
  --project projects/semi-ev3_20260403 \
  --prompt-file prompts/slide_01.txt \
  --output slides/slide_01.png \
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
├── META_PROMPT.md              # 通用元提示词模板
├── ComfyUI/                    # ComfyUI 工作流
├── scripts/                    # 通用脚本
│   └── core/                   # 核心脚本
│       ├── batch_generate_images.py
│       ├── batch_generate_prompts.py
│       └── ...
└── projects/                   # 项目目录
    └── semi-ev3_20260403/
        ├── META_PROMPT_PROJECT.md   # 项目元提示词模板
        ├── slides_content.md          # 幻灯片内容
        ├── prompts/                  # 提示词文件
        ├── slides/                   # 生成的图片
        ├── assets/                   # earch/             # 中间脚本
```

素材图片
        └── autores---

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

**版本**：v2.0 (2026-04-03)
**更新**：添加一页一页生成提示词的流程
