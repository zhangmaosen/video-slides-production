# Video Slides Production - 视频幻灯片生产技能

## 核心流程

```
a. 逐字稿 → slides内容（观点|逐字稿|背景知识）
b. 素材整理（图片、茂森IP）
c. 图片生成
   c1. 元提示词模板 + 逐字稿 + 背景知识 → 最终提示词（500+字）
   c2. 分工：Qwen Edit（真实产品）| Z-Image Turbo（其他）
   c3. 茂森IP：按需使用，非每页出现
   c4. 封面PIL添加文字
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
茂森：Q 版，蓬松黑发，八字浓眉，白色 T 恤，自信表情，穿着休闲
```

### 茂森语音参考
- 文件：`tmp-slides/maosen_voice_sample.mp4`

---

## c. 图片生成

### c1. 元提示词模板

**模板文件：** `META_PROMPT.md`

**模板核心规则：**
1. **风格绝对统一**：提取 1-2 个核心风格词放句首
2. **精简文字提取**：只提炼标题/观点/核心数据，用英文双引号包裹
3. **主体最详尽**：详尽描写材质、颜色、光影、数量、动作
4. **空间关系明确**：明确左右/前后/上下层级，指出留白
5. **绝对正向描述**：不用负面词汇，直接描述应该存在什么
6. **故事感核心**：冲突双方 + 动态动作 + 场景叙事 + 视觉张力 + 隐喻表达（避免孤零零的主角）
7. **中文输出**：所有提示词必须使用中文（除必要的英文品牌/术语）
8. **纯净静默输出**：只输出 prompt 文本，无任何解释/标题/注释

**详细文档：** 见 `META_PROMPT.md` (v5.0)

### 生成最终提示词流程

**输入：**
- 风格：`手绘漫画风格，线条粗细变化，水墨灰阶，诙谐严肃混合，混子说风格，舞台感构图`
- 逐字稿内容
- 背景知识

**处理流程：**
1. 实例化元模板：`PROMPT_TEMPLATE.format(输入风格=风格，输入内容=逐字稿 + 背景知识)`
2. AI 执行元模板，锁定核心要素
3. 生成式推理，构想完整画面方案
4. 注入美学细节
5. 文字用英文双引号框起来
6. **输出必须超过 500 字**

**输出：**
```
最终图片提示词（500+ 字，可直接用于图片生成）
```

### 批量生成脚本

**通用脚本**：`batch_generate_prompts.py`

**使用方式**：
```bash
cd skills/video-slides-production
python3 batch_generate_prompts.py \
  --project tmp-slides/semi-ev3 \
  --content-file slides_content.json \
  --output-dir prompts/v6 \
  --style "混子说风格融合硬核工程拆解素描风格" \
  --api-key "你的 API_KEY"
```

**参数说明**：
- `--project`: 项目名称（workspace 下的目录）
- `--content-file`: slides 内容文件（JSON 格式，相对于项目目录）
- `--output-dir`: 输出目录（相对于项目目录）
- `--style`: 视觉风格（可选，默认混子说风格）
- `--api-key`: API Key（可选，也可通过环境变量 MINIMAX_API_KEY 设置）

**slides_content.json 格式**：
```json
{
  "slide_00": {
    "title": "标题",
    "viewpoint": "观点",
    "script": "逐字稿",
    "background": "背景知识"
  },
  "slide_01": { ... },
  ...
}
```

**输出**：
- 每个 slide 生成一个 `.txt` 文件
- 保存到指定的 output-dir 目录
- 自动跳过已存在的文件

### 图片提示词生成（规则外置）

**元提示词模板：** `META_PROMPT.md`  
**条件规则配置：** `CONDITION_RULES.md`

**生成流程**：
```
用户输入 → 读取条件规则配置 → 判断触发规则 → 注入到元模板 → AI 生成 → 最终提示词
```

**架构优势**：
- ✅ **元模板通用**：META_PROMPT.md 保持纯净，不包含项目特定规则
- ✅ **规则可配置**：每个项目可以有独立的 CONDITION_RULES.md
- ✅ **易于维护**：修改规则无需改动元模板
- ✅ **版本控制**：用 Git 追踪规则变更

**Tesla Semi 项目规则**（见 `CONDITION_RULES.md`）：
- **规则 A**：Tesla Semi 特征（7 项，高优先级）
- **规则 B**：燃油卡车对比（6 项，中优先级）
- **规则 C**：充电场景（5 项，中优先级）
- **规则 D**：司机体验（7 项，低优先级）

**生成脚本**：`gen_prompts_v2.py`（支持条件规则动态注入）

**原则**：
- 条件规则是**配置文件**，不是硬编码在元模板中
- 每个项目可以自定义规则（复制 CONDITION_RULES.md 并修改）
- 规则优先级：高（核心产品）> 中（场景关键）> 低（辅助细节）

---

## d. ComfyUI 图片生成

### ComfyUI Qwen-Image API 客户端

**API 客户端**：`comfyui_api.py`

**类名**：`ComfyUIQwenImageAPI`

**功能**：
- 文本到图像生成（Qwen-Image-2512 模型）
- 支持 Lightning 模式（4 步快速生成）
- 支持标准模式（50 步高质量生成）
- 任务队列管理

**工作流配置**：
- 模型：`qwen_image_2512_fp8_e4m3fn.safetensors`
- CLIP: `qwen_2.5_vl_7b_fp8_scaled.safetensors`
- VAE: `qwen_image_vae.safetensors`
- LoRA: `Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors`（Lightning 模式）

**使用示例**：

```python
from comfyui_api import ComfyUIQwenImageAPI

# 初始化 API 客户端
api = ComfyUIQwenImageAPI("http://100.111.221.7:8188")

# 生成图像（Lightning 模式）
result = api.generate_image(
    prompt_text="一辆绿色的特斯拉 Semi 卡车",
    negative_prompt="低分辨率，低画质，肢体畸形",
    width=1328,
    height=1328,
    seed=None,  # 随机种子
    use_lightning=True,  # Lightning 模式
    filename_prefix="slide_00"
)
# 输出：✅ 任务已提交：xxx
#       模式：Lightning (4 步)
#       分辨率：1328x1328
#       种子：1234567890

# 生成图像（标准模式）
result = api.generate_image(
    prompt_text="一辆绿色的特斯拉 Semi 卡车",
    use_lightning=False,  # 标准模式（50 步）
    filename_prefix="slide_00_standard"
)
```

**API 方法**：

| 方法 | 参数 | 说明 |
|------|------|------|
| `generate_image()` | `prompt_text` | 正提示词 |
| | `negative_prompt` | 负提示词（可选） |
| | `width` | 图像宽度（默认 1280） |
| | `height` | 图像高度（默认 800） |
| | `seed` | 随机种子（None 表示随机） |
| | `use_lightning` | Lightning 模式开关（默认 False） |
| | `filename_prefix` | 输出文件名前缀 |

**返回结果**：
```python
{
    "prompt_id": "xxx-xxx-xxx",
    "seed": 1234567890,
    "use_lightning": True,
    "status": "queued",
    "error": None
}
```

### 图片编辑（基于参考图）

**功能**：使用 Qwen-Image-Edit-2509 模型进行图片编辑

**工作流配置**：
- 模型：`qwen_image_edit_2509_fp8_e4m3fn.safetensors`
- CLIP: `qwen_2.5_vl_7b_fp8_scaled.safetensors`
- VAE: `qwen_image_vae.safetensors`
- LoRA: `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors`

**使用示例**：

```python
from comfyui_api import ComfyUIQwenImageAPI

# 初始化 API 客户端
api = ComfyUIQwenImageAPI("http://100.111.221.7:8188")

# 图片编辑（绿身替换）
result = api.edit_image(
    input_image_path="green_car.png",  # 输入图片（要编辑的图片）
    reference_image_path="truck_reference.png",  # 参考图片（替换内容的参考）
    edit_prompt="将图 1 中的绿色卡车替换成图 2 中的特斯拉 Semi 卡车，保留图 1 的其他画面",
    filename_prefix="test_edit"
)
# 输出：✅ 编辑任务已提交：xxx
#       输入图片：green_car.png
#       参考图片：truck_reference.png
#       编辑提示：将图 1 中的绿色卡车替换成图 2 中的特斯拉 Semi 卡车...
```

**API 方法**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `input_image_path` | str | 输入图片路径（要编辑的图片，如绿身图片） |
| `reference_image_path` | str | 参考图片路径（替换内容的参考，如真实产品图） |
| `edit_prompt` | str | 编辑提示词（描述如何编辑） |
| `seed` | int | 随机种子（None 表示随机） |
| `filename_prefix` | str | 输出文件名前缀 |

**返回结果**：
```python
{
    "prompt_id": "xxx-xxx-xxx",
    "seed": 1234567890,
    "input_image": "green_car.png",
    "reference_image": "truck_reference.png",
    "status": "queued",
    "error": None
}
```

**编辑提示词示例**：
- "将图 1 中的绿色卡车替换成图 2 中的特斯拉 Semi 卡车，保留图 1 的其他画面"
- "把图 1 中的车辆替换成图 2 中的卡车，保持场景和光线不变"
- "用图 2 的产品替换图 1 中的绿色物体，保留背景"

### 批量生成图片

**批量生成脚本**：`batch_generate_images.py`

**使用方式**：
```bash
cd skills/video-slides-production
python3 batch_generate_images.py \
  --prompts-dir tmp-slides/semi-ev3/prompts/v6 \
  --output-dir tmp-slides/semi-ev3/slides \
  --lightning \
  --comfyui-url http://100.111.221.7:8188
```

**参数说明**：
- `--prompts-dir`: 提示词目录（包含多个 .txt 文件）
- `--output-dir`: 输出目录（ComfyUI 服务器输出位置）
- `--lightning`: 使用 Lightning 模式（4 步快速生成）
- `--comfyui-url`: ComfyUI 服务器地址

**输出**：
- 每个提示词文件生成一个任务
- 提交到 ComfyUI 队列
- 返回任务 ID 和状态

### 下载生成的图片

**下载脚本**：`download_images.py`

**使用方式**：
```bash
cd skills/video-slides-production
python3 download_images.py
```

**功能**：
- 自动从 ComfyUI 历史获取文件名
- 批量下载所有生成的图片
- 保存到本地目录

**输出位置**：
```
tmp-slides/semi-ev3/slides/
├── slide_00_00003_.png
├── slide_01_00002_.png
├── ...
└── slide_16_00001_.png
```

### 生成模式对比

| 模式 | 步数 | 耗时 | 质量 | 适用场景 |
|------|------|------|------|----------|
| Lightning | 4 步 | ~24 秒 | 高 | 快速迭代、批量生成 |
| 标准 | 50 步 | ~5 分钟 | 最高 | 最终成品、高质量需求 |

**Lightning 模式特点**：
- 使用 LoRA: `Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors`
- 自动切换 steps=4, cfg=1
- 生成速度快，质量接近标准模式

**标准模式特点**：
- 不使用 LoRA
- steps=50, cfg=4
- 生成速度慢，质量最高

```

**参数说明**：
- `--prompts-dir`: 提示词目录（例如：prompts/v6）
- `--output-dir`: 输出目录
- `--lightning`: 使用 Lightning 模式（4 步快速生成，约 24 秒/张）
- `--no-lightning`: 使用标准模式（50 步，约 5 分钟/张）
- `--comfyui-url`: ComfyUI API 地址

**工作流程**：
1. 读取 `prompts-dir` 下的所有 `slide_*.txt` 文件
2. 调用 ComfyUI API 批量生成图片
3. 提交任务并显示进度
4. 生成完成后在 ComfyUI 输出目录查找图片

**输出**：
- 图片保存到 ComfyUI 的 `output/` 目录
- 文件名格式：`{slide_name}_0.png`

### 配置文件

**ComfyUI 配置**：`comfyui_config.json`
```json
{
  "base_url": "http://100.111.221.7:8188",
  "default_mode": "lightning",
  "resolution": {
    "width": 1280,
    "height": 800
  }
}
```

**工作流文件**：
- `Qwen-Image-2512_ComfyUI.json` - 完整工作流
- `Qwen-Image-2512_Simple.json` - 简化工作流
- `Qwen-Image-2512_Workflow.json` - 标准工作流

### 生成参数

**标准模式**：
- Steps: 50
- CFG: 4
- Sampler: euler
- 分辨率：1280×800 (16:9)
- 速度：约 5 分钟/张

**Lightning 模式**（快速）：
- Steps: 4
- CFG: 1
- 启用 LoRA: `Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors`
- 分辨率：1280×800 (16:9)
- 速度：约 24 秒/张

**图像编辑模式**（绿身替换）：
- 模型：`qwen_image_edit_2509_fp8_e4m3fn.safetensors`
- LoRA: `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors`
- Steps: 4
- CFG: 1
- 提示词："把图 1 中的绿色卡车改成图 2 的卡车"

### c2. 分工

| 场景 | 工作流 | 说明 |
|------|--------|------|
| 封面（真实产品对比） | Qwen Image Edit | + PIL 添加文字 |
| 需要真实产品的页面 | Qwen Image Edit | Prompt 写"不要添加任何文字" |
| 抽象/概念/人物/场景 | Z-Image Turbo | AI 自由发挥 |
| 信息图/地图/图表 | Z-Image Turbo | AI 生成 |

### c3. 茂森 IP 使用原则

**原则：**
- ✅ 茂森仅在必要时出现
- ✅ 茂森必须出现：封面、结尾
- ✅ 茂森可选出现：需要人物引导或对比的页面
- ❌ 大部分页面不需要茂森
- ❌ 不要每页都加茂森
- ❌ 不要在元模板中预设茂森出现

**茂森出现条件：**
- 页面需要人物引导或情感表达时
- 页面需要对比或解说时
- 封面和结尾（必须）

**其他页面：让数据和内容自己说话**

### c4. 封面处理

**方案 A：AI 生成带文字（推荐）**
- 在 prompt 中明确要求文字内容
- 使用 Qwen-Image-2512 标准模式（50 步）
- 文字要求必须具体明确（见示例）
- 需要 autoresearch 迭代优化到 95 分+

**方案 B：PIL 添加文字（备选）**
- AI 生成无文字底图
- PIL 添加主标题、副标题、数据标注
- 适用于文字要求复杂或 AI 生成不稳定的情况

**AI 文字生成最佳实践**（Tesla Semi 项目经验）：
1. **明确文字要求**：在 prompt 中逐字写出需要显示的文字
2. **指定位置**：明确每个文字的位置（顶部中央、右下角等）
3. **指定样式**：说明字体大小、颜色、粗细
4. **强调准确性**："必须清晰可读，无错别字，无乱码"
5. **迭代优化**：如果文字乱码，调整 prompt 继续生成，不要放弃

**示例 prompt**：
```
【文字标注要求 - 必须清晰可读，无错别字，无乱码】

**位置 1：画面顶部中央**
- 主标题："特斯拉 Semi 掀翻燃油卡车"（大号粗体，黑色）
- 副标题："全球商用货运革命的开启"（中号字体，深灰色，位于主标题正下方）

**位置 2：画面右下角**
- "200 万"（绿色粗体）
- "千亿市场"（绿色粗体，位于"200 万"正下方）

**位置 3：Tesla Semi 车身周围（用细黑线引出标注框）**
- "三电机动力总成"（指向底盘）
- "1000V 高压架构"（指向车身中部）
- "0.36 风阻系数"（指向车头）
- "中置驾驶席"（指向驾驶舱）
- "3 轴 6 轮配置"（指向车轮）

【关键要求】
1. 所有文字必须使用标准简体中文，无错别字
2. 文字必须清晰可读，不能使用艺术字体或变形字体
3. 标注框必须是矩形，黑色细线边框
4. 主副标题必须完整准确，一个字都不能错
```

### 风格标签
```
手绘漫画风格，线条粗细变化，水墨灰阶，诙谐严肃混合，混子说风格，舞台感构图
```

---

### c5. 评分机制

**核心原则：每一步打分都用独立 subagent 来完成**

**详细文档：** 见 `SCORING.md`

**关键点：**
- ✅ subagent 名称：**二郎神**（天眼通，洞察一切细节）
- ✅ **逐字稿必须提供**：让二郎神逐字核对，一个字都不能错
- ✅ **参考图片必须提供**：让二郎神逐项对比，不能凭印象
- ✅ **82 分通过标准**：达到 82 分即可通过（A 级），95 分是 S 级但不是必须
- ✅ **正向 + 负向提示词双管齐下**：这是解决文字问题的关键
- ✅ **字体放大**：字体越大，出错概率越低（主标题 85px+，副标题 50px+）
- ✅ **减少文字**：不要每页都有标题，除非逐字稿明确；只保留核心数据
- ✅ **逐字稿优先**：只有逐字稿中明确要求的文字才需要评分；如果没有要求，默认得分

**评分标准（2026-04-03 更新）：**
- **文字准确性**：40 分（主标题 20 分 + 副标题/数据 20 分，逐字稿有要求才评分）
- 故事性和自说明性：20 分
- 参考物神似度：20 分
- 视觉吸引力：10 分
- 风格一致性：10 分
- **总分**：100 分（**通过标准：82 分+**，S 级：95-100 分）

**等级划分：**
- S 级：95-100 分（完美）
- **A 级：82-94 分（✅ 通过标准）**
- B 级：70-81 分（需要调整）
- C 级：60-69 分（需要大改）
- F 级：<60 分（重新生成）

**Tesla Semi 项目经验：**
- v1-v9：文字问题持续，评分 49-97 分波动
- v10：**正向 + 负向提示词双管齐下**，文字 100% 准确（30/30 分）
- v11-v12：文字再次失控（"绝美核比"、"两系"、"Tesle"等）
- **最终：v12 = 82 分（✅ 达到通过标准）**
- **经验：12 次迭代才达到 82 分，文字准确性是最大挑战**

---

## d. TTS 生成

### 茂森语音克隆
- 参考音频：`tmp-slides/maosen_voice_sample.mp4`
- 用于 VoiceClone 生成 TTS 音频

### 生成方式
- ComfyUI VoiceDesign → VoiceClone（使用茂森语音样本）

---

## e. 视频合成

### 工具
- FFmpeg：字幕叠加、音视频合成

### 参数
- 分辨率：1280×720（16:9）
- 帧率：30fps
- 音频：AAC

---

## 项目结构

**每个视频项目必须创建独立文件夹！**

```
{project_name}_{YYYYMMDD}/
├── script.md             # 逐字稿
├── slides_content.md     # 格式化后的 slides 内容
├── prompts.md            # 最终提示词
├──素材/                  # 原始素材图片
│   ├── tesla_semi.jpg
│   ├── windrose.jpg
│   └── ...
├── slides/             # 幻灯片图片
│   ├── slide_00.png    # 封面
│   └── slide_*.png
├── audio/              # TTS 音频
│   └── seg_*.m4a
├── overlays/          # 字幕 overlay
├── final/             # 最终视频
│   └── final.mp4
└── gen_*.py          # 生成脚本
```

**命名规范：**
- 文件夹：`{项目名}_{日期}`，如 `semi_20260331`
- 幻灯片：`slide_00.png` ~ `slide_XX.png`
- 音频：`seg_00.m4a` ~ `seg_XX.m4a`

---

## 评分标准（Slide 图片质量）

### 评分维度

#### 1. 逐字稿遵循度（30 分）⭐ 最重要

**标题准确性（15 分）**：
| 分数 | 标准 |
|------|------|
| 15 | 完美 - 主标题 + 副标题 100% 准确，无错别字 |
| 12-14 | 优秀 - 主标题准确，副标题 1 个非关键错字 |
| 9-11 | 良好 - 主标题准确，副标题有少量缺失 |
| 6-8 | 及格 - 主标题有 1 个错字，副标题不完整 |
| 0-5 | 不合格 - 主标题缺失、严重错别字或完全错误 |

**其他元素（15 分）**：
| 分数 | 标准 |
|------|------|
| 15 | 完美 - 所有标注、数据、位置 100% 符合 |
| 12-14 | 优秀 - 标注完整，1 个非关键位置偏差 |
| 9-11 | 良好 - 主要标注完整，缺少 1-2 个次要标注 |
| 6-8 | 及格 - 缺少部分标注或数据 |
| 0-5 | 不合格 - 多处缺失或错误 |

#### 2. 故事性和自说明性（20 分）
| 分数 | 标准 |
|------|------|
| 20 | 完美 - 3 秒内就能完全理解核心观点 |
| 16-19 | 优秀 - 5 秒内理解，构图清晰 |
| 12-15 | 良好 - 需要 10 秒思考才能理解 |
| 8-11 | 及格 - 需要辅助说明 |
| 0-7 | 不合格 - 很难理解想表达什么 |

#### 3. 参考物神似度（20 分）
| 分数 | 标准 |
|------|------|
| 20 | 完美 - 所有关键特征 100% 准确 |
| 16-19 | 优秀 - 关键特征准确，细节有微小偏差 |
| 12-15 | 良好 - 主要特征正确，缺少 1-2 个关键细节 |
| 8-11 | 及格 - 能看出相似，但关键特征有缺失 |
| 0-7 | 不合格 - 关键特征错误（如轴数、颜色等） |

#### 4. 技术准确性（15 分）
| 分数 | 标准 |
|------|------|
| 15 | 完美 - 所有参数 100% 准确 |
| 12-14 | 优秀 - 参数准确，标注位置有微小偏差 |
| 9-11 | 良好 - 大部分正确，1 个次要参数有误 |
| 6-8 | 及格 - 关键参数有误（如风阻系数、电压等） |
| 0-5 | 不合格 - 多处技术错误或误导读者 |

#### 5. 视觉吸引力（10 分）
| 分数 | 标准 |
|------|------|
| 9-10 | 构图优秀，色彩协调，冲击力强 |
| 7-8 | 整体美观，无明显缺陷 |
| 5-6 | 中规中矩，缺乏亮点 |
| 3-4 | 视觉混乱，配色不当 |
| 0-2 | 严重影响观看体验 |

#### 6. 风格一致性（5 分）
| 分数 | 标准 |
|------|------|
| 5 | 完全符合混子说手绘风格 |
| 4 | 基本符合，细节略有偏差 |
| 3 | 部分符合 |
| 2 | 风格混杂 |
| 0-1 | 完全偏离 |

### 评分等级

| 总分 | 等级 | 说明 |
|------|------|------|
| 95-100 | **S 级** | 完美，可直接使用 |
| 90-94 | A 级 | 优秀，微调后可用 |
| 80-89 | B 级 | 良好，需要修改 |
| 70-79 | C 级 | 及格，大幅修改 |
| 60-69 | D 级 | 较差，建议重做 |
| 0-59 | F 级 | 不合格，必须重做 |

### 一票否决项（直接 F 级）
1. **主标题缺失或错误**
2. **副标题缺失或错误**
3. **文字错别字超过 3 处**
4. **技术参数严重错误**

### autoresearch 优化流程

**目标**：通过迭代优化达到 95 分+（S 级）

**流程**：
1. 生成 v1 版本 → 2. 评分 → 3. 分析扣分点 → 4. 调整 prompt → 5. 生成 v2 → 6. 重复直到 95 分+

**关键原则**：
- ✅ 评分标准不变
- ✅ 只修改 prompt，不修改评分规则
- ✅ 持续迭代直到满足得分标准
- ✅ 文字问题不要放弃，调整 prompt 继续尝试

**Tesla Semi 项目经验**：
- v1-v5：文字缺失/乱码（60-80 分）
- v6-v8：去掉文字，专注画面（91-97.5 分）
- v9：尝试文字但乱码（60 分）
- **v10：文字 + 画面双完美（100 分）**

**经验总结**：
- AI 可以生成准确文字，但需要明确具体的 prompt
- 不要过早放弃文字生成，调整 prompt 可能解决问题
- 标准模式（50 步）比 Lightning 模式文字质量更好

---

## 注意事项

### 避免
- 光头、单一姿势/表情
- 解说员占据太多画面
- 粗暴加入人物角色风格提示词

### 茂森 IP
- 用提示词描述，不合并真实图片
- 根据内容需要决定出现位置
- 让内容自己表达
