# Video Slides Production

视频幻灯片生产技能。

## 核心文档

| 文件 | 行数 | 说明 |
|------|------|------|
| [SKILL.md](SKILL.md) | 715 | 主文档，完整工作流程 |
| [SCORING.md](SCORING.md) | 199 | 评分机制（二郎神 subagent） |
| [META_PROMPT.md](META_PROMPT.md) | 129 | 元提示词模板 |
| [CONDITION_RULES.md](CONDITION_RULES.md) | 120 | 条件规则配置 |
| [POST_PROCESS_RULES.md](POST_PROCESS_RULES.md) | 189 | 后处理规则 |

## 核心流程

```
a. 逐字稿 → slides 内容（观点 | 逐字稿 | 背景知识）
b. 素材整理（图片、茂森 IP）
c. 图片生成
   c1. 元提示词模板 + 逐字稿 + 背景知识 → 最终提示词（500+ 字）
   c2. 分工：Qwen Edit（真实产品）| Z-Image Turbo（其他）
   c3. 茂森 IP：按需使用，非每页出现
   c4. 封面 PIL 添加文字
d. TTS 生成（茂森语音 Clone）
e. FFmpeg 视频合成
```

## 评分标准

**通过标准：82 分+（A 级）**

| 等级 | 分数 | 说明 |
|------|------|------|
| S | 95-100 | 完美 |
| A | 82-94 | ✅ 通过标准 |
| B | 70-81 | 需要调整 |
| C | 60-69 | 需要大改 |
| F | <60 | 重新生成 |

**评分维度：**
- 文字准确性：40 分（主标题 20 分 + 副标题/数据 20 分）
- 故事性和自说明性：20 分
- 参考物神似度：20 分
- 视觉吸引力：10 分
- 风格一致性：10 分

**评分机制：**
- 每一步打分都用**独立 subagent（二郎神）**来完成
- 逐字稿必须提供（逐字核对）
- 参考图片必须提供（逐项对比）
- 82 分通过标准（A 级）

## 目录结构

```
video-slides-production/
├── README.md              # 总项目说明
├── SKILL.md              # 主文档
├── SCORING.md            # 评分机制
├── META_PROMPT.md        # 元提示词模板
├── scripts/              # 脚本
│   ├── batch_generate_prompts.py
│   ├── batch_generate_images.py
│   ├── comfyui_api.py
│   └── ...
├── ComfyUI/              # ComfyUI 工作流
│   ├── Qwen-Image-2512_ComfyUI.json
│   └── ...
└── projects/             # 项目目录
    └── {project_name}_{YYYYMMDD}/
        ├── script.md
        ├── slides_content.md
        ├── prompts.md
        ├── 素材/
        ├── slides/
        ├── audio/
        ├── overlays/
        ├── final/
        └── gen_*.py
```

## 项目结构（每个视频项目）

**每个视频项目必须创建独立文件夹！**

```
{project_name}_{YYYYMMDD}/
├── script.md             # 逐字稿
├── slides_content.md     # 格式化后的 slides 内容
├── prompts.md            # 最终提示词
├──素材/                  # 原始素材图片
├── slides/               # 幻灯片图片
├── audio/                # TTS 音频
├── overlays/             # 字幕 overlay
├── final/                # 最终视频
└── gen_*.py              # 生成脚本
```

**命名规范：**
- 文件夹：`{项目名}_{日期}`，如 `semi_ev3_20260403`
- 幻灯片：`slide_00.png` ~ `slide_XX.png`
- 音频：`seg_00.m4a` ~ `seg_XX.m4a`

## 技术栈

- **图片生成**：ComfyUI + Qwen-Image-2512
- **评分机制**：二郎神 subagent（独立评分）
- **TTS**：Qwen TTS
- **视频合成**：FFmpeg

## 最佳实践

- ✅ 正向 + 负向提示词双管齐下
- ✅ 字体放大（主标题 85px+，副标题 50px+）
- ✅ 减少文字（不要每页都有标题，除非逐字稿明确）
- ✅ 逐字稿优先（只有逐字稿中明确要求的文字才需要评分）
- ✅ 二郎神独立评分（不受上下文干扰）

## Tesla Semi 项目经验

- **12 次迭代**才达到 82 分
- **文字准确性是最大挑战**（AI 文字生成能力不稳定）
- **v10 曾经达到 30/30 分**（文字 100% 准确），但 v11、v12 再次失控
- **82 分是务实的通过标准**（平衡质量和效率）

---

**最后更新：** 2026-04-03  
**版本：** v1.0  
**作者：** 茂森
