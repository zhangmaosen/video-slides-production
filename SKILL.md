# Video Slides Production - 视频幻灯片生产技能

---

## 🚀 欢迎使用视频幻灯片制作技能！

我来帮你把报告文档转化为吸引人的视频幻灯片。

---

## 📋 项目配置向导

### 1️⃣ 请提供项目名称
```
例如：Tesla Semi 分析报告
```

### 2️⃣ 请提供报告文档
```
你可以：
- 直接粘贴报告内容
- 或提供文件路径
```

### 3️⃣ 选择视觉风格
```
a) 混子说 + 硬核工程拆解爆炸图风格
b) 电影级写实
c) 赛博朋克
d) 自定义
```

### 4️⃣ 是否有参考图？
```
- 有（请上传或指定路径）
- 无
```

### 5️⃣ 是否使用茂森 IP？
```
- 是
- 否
```

### 6️⃣ 茂森语音参考
```
- 有（请提供音频文件）
- 无
```

### 7️⃣ 输出分辨率
```
默认：1280x800（16:9）
可选：1920x1080 / 1080x1920 等
```

---

## ✅ 配置确认

完成后，我会：

1. **仓颉** 整理内容 → `slides_content.json`
2. **女娲** 生成提示词 → `prompts/slide_XX/`
3. **哪吒** 生成图片 → `slides/slide_XX.png`
4. **二郎神** 评分（10次迭代选最高）
5. **TTS** 生成语音
6. **FFmpeg** 合成视频

---

## 角色分工

| 角色 | 职责 | 执行者 |
|------|------|--------|
| **仓颉** | 报告 → 逐字稿 | Agent |
| **女娲** | 生成和优化 prompt | Agent |
| **哪吒** | 生成图片 | Agent |
| **二郎神** | 评分（10次迭代选最高） | Agent |
| **Rex** | 协调循环、记录、决策 | 人类/Rex |

---

## 核心流程

```
a. 报告文档 → slides_content.json（仓颉）
b. 素材整理（图片、茂森IP）
c. Autoresearch Loop（最多10次）
d. TTS生成
e. FFmpeg视频合成
```

---

## 评分标准（100分）

| 维度 | 分值 |
|------|------|
| 文字准确性 | 30分 |
| 参考对象准确性 | 40分 |
| 故事表达能力 | 30分 |

---

## 项目结构

```
video-slides-production/
├── SKILL.md                     # 本文档
├── SCORING.md                   # 评分标准
├── SYSTEM_PROMPT.md             # 女娲 System Prompt
├── SYSTEM_PROMPT_CANGJIE.md    # 仓颉 System Prompt
├── AUTORESEARCH_LOOP.md        # Autoresearch 循环流程
├── ComfyUI/                   # ComfyUI 工作流
├── scripts/
│   └── core/
│       └── gen_slide.py        # 生成图片脚本
└── projects/
    └── [项目名]/
        ├── project_config.json      # 项目配置
        ├── slides_content.json     # 幻灯片内容
        ├── script.md               # 原始报告
        ├── prompts/               # 提示词（版本化）
        │   └── slide_XX/
        │       ├── v1_positive.txt
        │       ├── v1_negative.txt
        │       └── CHANGELOG.md
        └── slides/                # 生成的图片
```

---

## 常用命令

### 检查 ComfyUI 状态
```bash
curl http://100.111.221.7:8188/system_stats
```

### 生成单张图片
```bash
python3 scripts/core/gen_slide.py \
  --project projects/[项目名] \
  --slide 00 \
  --version 1
```

---

**版本**：v6.0 (2026-04-04)
**更新**：添加用户引导流程，仓颉支持报告文档转逐字稿
