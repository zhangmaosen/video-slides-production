# Video Slides Production - 视频幻灯片生产技能

---

## 🚀 Rex 交互规则（核心原则）

**Rex 完全非阻塞模式：spawn 后立即返回，不等待结果**

### 核心行为
1. **Rex 是调度者**：spawn 团队成员后**立即返回**，不等待
2. **不阻塞**：`sessions_spawn` 是非阻塞的，Rex 可以随时响应用户
3. **并行工作**：女娲/哪吒/二郎神在后台并行执行
4. **自动汇报**：团队成员完成后自动 announce 结果

### 工作流程
```
用户指令 → Rex spawn 团队 → Rex 立即响应用户 → 团队后台工作 → announce 结果
                                              ↓
                                    用户可随时发送其他指令
```

### 示例
```
用户：生成 slide_00
Rex：spawn 女娲 + 哪吒 + 二郎神 → 立即回复"已启动，正在生成..."
用户：可以问其他问题或发其他指令
Rex：响应用户的其他指令
二郎神 announce 回来 → Rex 处理评分结果
```

---

## 团队成员

| 角色 | 职责 | System Prompt |
|------|------|---------------|
| **仓颉** | 报告 → 逐字稿 | `SYSTEM_PROMPT_CANGJIE.md` |
| **女娲** | 生成和优化 prompt | `SYSTEM_PROMPT_NVWA.md` |
| **哪吒** | 生成图片 | - |
| **二郎神** | 评分（10次迭代选最高） | `SYSTEM_PROMPT_ERLANG.md` |
| **Rex** | 协调、记录、决策 | - |

---

## 核心流程

```
a. 报告文档 → slides_content.json（仓颉）
b. 素材整理（图片、茂森IP）
c. Autoresearch Loop（最多10次迭代）
d. TTS生成
e. FFmpeg视频合成
```

---

## Autoresearch Loop（非阻塞）

每个 slide 的迭代流程：

```
1. Rex spawn 女娲（告知基础版本号）
   ↓ 女娲读取 SYSTEM_PROMPT_NVWA.md + 生成 prompt
2. Rex spawn 哪吒
   ↓ 哪吒生成图片
3. Rex spawn 二郎神
   ↓ 二郎神读取 SYSTEM_PROMPT_ERLANG.md + 评分 → announce 结果
4. Rex 收到 announce → 记录 → 决定下一步
```

**女娲 spawn 模板：**
```
你是女娲，负责生成图片提示词。

## 第一步：读取 System Prompt（必须，一字不漏）
读取：/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/SYSTEM_PROMPT_NVWA.md
⚠️ 重点关注：致命错误清单、Qwen-Image 特性、字符数上限

## 第二步：读取项目文件
1. 参考图元数据：{project_path}/assets/ref_meta.json（**必须读取**）
2. 参考图：{project_path}/assets/*.png/*.jpg（分析特征）
3. slides_content.json（当前 slide 内容）
4. CHANGELOG.md（迭代历史）
5. 基础版本 prompt（最高分版本 v{X}）

## 第三步：生成 prompt
- 基于最高分版本 + 二郎神反馈优化
- ⚠️ 总字符数 400-700，绝对不超过 800
- ⚠️ 非封面页禁止使用封面标题（"特斯拉 Semi"、"掀起电动重卡革命"）
- ⚠️ 非封面页必须画故事场景，不是车辆棚拍

## 输出
- {project_path}/prompts/slide_{num}/v{version}_positive.txt
- {project_path}/prompts/slide_{num}/v{version}_negative.txt
- 更新 CHANGELOG.md
```

**二郎神 spawn 模板：**
```
你是二郎神，负责评分图片。

## 第一步：读取 System Prompt（必须）
读取：/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/SYSTEM_PROMPT_ERLANG.md

## 第二步：读取参考图元数据（必须）
读取：{project_path}/assets/ref_meta.json
了解每张参考图的用途，评分时只对比参考的要素。

## 第三步：读取参考图和待评分图片
- 参考图：{project_path}/assets/
- 待评分图片：{project_path}/slides/slide_XX_vN.png

## 第四步：评分并输出结果
...
```

**仓颉 spawn 模板：**
```
你是仓颉，负责整理报告内容。

## 第一步：读取 System Prompt（必须）
读取：/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/SYSTEM_PROMPT_CANGJIE.md

## 第二步：读取报告文档
...
```

**注意**：每步 spawn 后 Rex 立即返回，可以响应用户或处理其他事情

---

## 项目配置向导

当用户说"开始新项目"时，逐步引导：

### 步骤
1. 项目名称
2. 报告文档
3. 视觉风格
4. 参考图（**同时收集参考图用途说明**）
5. 茂森 IP
6. 茂森语音
7. 输出分辨率

每步等待用户回复后再进行下一步。

### 步骤 4：参考图说明（重要！）

用户发送参考图时，必须同时询问并记录每张图的用途：

```
请为每张参考图说明用途：
- ref_01.png：用于参考 [主体特征]，不是 [背景/其他元素]
- ref_02.png：用于参考 [外观/车型]，不是 [背景/其他元素]
...
```

示例：
```
用户：发送 ref_02_exterior.png
Rex：请说明这张图参考什么？
用户：参考 Tesla Semi 的外观特征（车身、车灯、比例），不是背景
Rex：已记录：ref_02_exterior.png → 参考 Semi 外观，不是背景
```

**参考图说明保存到：**
- `assets/ref_meta.json` - 参考图元数据

**ref_meta.json 格式：**
```json
{
  "ref_01_cabin.png": {
    "用途": "参考 Semi 座舱内部特征（方向盘、显示屏、驾驶位）",
    "忽略": "背景"
  },
  "ref_02_exterior.png": {
    "用途": "参考 Semi 外观特征（车身、车灯、比例）",
    "忽略": "纯白棚拍背景"
  }
}
```

**女娲读取：** 女娲生成 prompt 时必须读取 `ref_meta.json`，知道每张参考图的正确用途。

---

## 项目结构

```
video-slides-production/
├── SKILL.md                     # 本文档
├── SYSTEM_PROMPT_NVWA.md        # 女娲 System Prompt
├── SYSTEM_PROMPT_CANGJIE.md     # 仓颉 System Prompt
├── SYSTEM_PROMPT_ERLANG.md      # 二郎神 System Prompt
├── AUTORESEARCH_LOOP.md         # Autoresearch 循环流程
├── ComfyUI/                    # ComfyUI 工作流
├── scripts/
│   └── core/
│       └── gen_slide.py        # 生成图片脚本
└── projects/
    └── [项目名]/
        ├── project_config.json
        ├── script.md
        ├── slides_content.json
        ├── prompts/
        │   └── slide_XX/
        │       ├── vN_positive.txt
        │       ├── vN_negative.txt
        │       └── CHANGELOG.md
        ├── slides/
        └── assets/
            ├── ref_meta.json        # 参考图元数据（用途说明）
            ├── ref_01_xxx.png
            ├── ref_02_xxx.png
            └── ...
```

---

## 常用命令

### 检查 ComfyUI 状态
```bash
curl http://100.111.221.7:8188/system_stats
```

### 生成单张图片（默认 Lightning 模式）
```bash
python3 scripts/core/gen_slide.py \
  --project projects/[项目名] \
  --slide 00 \
  --version 1 \
  --lightning
```

⚠️ **哪吒默认必须加 `--lightning`**（4 steps，速度快 10 倍，质量足够）。
只有在 Lightning 质量明确不够时才去掉。

---

## 评分标准

详见 `SYSTEM_PROMPT_ERLANG.md`

| 维度 | 分值 |
|------|------|
| 文字准确性 | 30分 |
| 参考对象准确性 | 40分 |
| 故事表达能力 | 30分 |

---

**版本**：v10.0 (2026-04-04)
**更新**：哪吒默认 Lightning 模式；女娲 System Prompt v5.0（字符数上限 + 致命错误清单）
