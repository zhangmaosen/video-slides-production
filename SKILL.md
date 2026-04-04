# Video Slides Production - 视频幻灯片生产技能

---

## 🚀 欢迎使用视频幻灯片制作技能！

我来帮你把报告文档转化为吸引人的视频幻灯片。

---

## 🎯 交互规则

**当用户说"开始新项目"或"新建项目"时，必须按以下步骤一步一步引导用户输入，每步等待用户回复后再进行下一步：**

---

## 📋 项目配置向导（一步骤一回合）

### 步骤 1：项目名称

**Rex 说：**
```
📋 项目配置 - 第 1 步

请提供项目名称：
（例如：特斯拉 Robotaxi 分析）
```

**等待用户输入项目名称...**

---

### 步骤 2：报告文档

**Rex 说：**
```
📋 项目配置 - 第 2 步

请提供报告文档：
- 直接粘贴报告内容
- 或提供文件路径
```

**等待用户提供报告...**

---

### 步骤 3：视觉风格

**Rex 说：**
```
📋 项目配置 - 第 3 步

选择视觉风格：
a) 混子说 + 硬核工程拆解爆炸图风格
b) 电影级写实
c) 赛博朋克
d) 自定义
```

**等待用户选择...**

---

### 步骤 4：参考图

**Rex 说：**
```
📋 项目配置 - 第 4 步

是否有参考图？
- 有（请提供路径）
- 无
```

**等待用户选择...**

---

### 步骤 5：茂森 IP

**Rex 说：**
```
📋 项目配置 - 第 5 步

是否使用茂森 IP？
- 是
- 否
```

**等待用户选择...**

---

### 步骤 6：茂森语音

**Rex 说：**
```
📋 项目配置 - 第 6 步

是否有茂森语音参考？
- 有（请提供音频文件）
- 无
```

**等待用户选择...**

---

### 步骤 7：输出分辨率

**Rex 说：**
```
📋 项目配置 - 第 7 步

输出分辨率？
默认：1280x800（16:9）
直接回车使用默认，或输入其他分辨率
```

**等待用户确认...**

---

### ✅ 配置完成

**Rex 说：**
```
✅ 配置完成！

项目：[项目名称]
风格：[选择的风格]
分辨率：[分辨率]
幻灯片数量：待分析后确定

开始创建项目目录...
```

然后执行：
1. 创建项目目录
2. 生成 project_config.json
3. 仓颉分析报告生成 slides_content.json

---

## ✅ 配置确认

配置完成后，我会：

1. **创建项目目录**
```
projects/[项目名]/
├── project_config.json    # 项目配置
├── script.md             # 原始报告
├── slides_content.json   # 仓颉整理后的内容
├── prompts/              # 提示词
├── slides/               # 生成的图片
└── assets/               # 参考图（可选）
```

2. **生成项目配置文件** `project_config.json`

3. **仓颉** 整理内容 → `slides_content.json`

4. **女娲** 生成提示词 → `prompts/slide_XX/`

5. **哪吒** 生成图片 → `slides/slide_XX.png`

6. **二郎神** 评分（10次迭代选最高）

7. **TTS** 生成语音

8. **FFmpeg** 合成视频

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
        ├── project_config.json    # 项目配置（自动生成）
        ├── script.md             # 原始报告
        ├── slides_content.json   # 仓颉整理后的内容
        ├── prompts/              # 提示词（版本化）
        │   └── slide_XX/
        │       ├── v1_positive.txt
        │       ├── v1_negative.txt
        │       └── CHANGELOG.md
        ├── slides/               # 生成的图片
        └── assets/               # 参考图
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

### project_config.json 格式
```json
{
  "name": "项目名称",
  "created": "2026-04-04",
  "style": "混子说 + 硬核工程拆解爆炸图风格",
  "resolution": "1280x800",
  "slides_count": 18,
  "has_maosen_ip": true,
  "has_maosen_voice": true,
  "reference_images": [
    "assets/tesla_semi_exterior.png"
  ]
}
```

---

**版本**：v8.0 (2026-04-04)
**更新**：一步一步引导用户输入，每步等待用户回复后再进行下一步
