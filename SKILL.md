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
   ↓ 女娲生成 prompt
2. Rex spawn 哪吒
   ↓ 哪吒生成图片
3. Rex spawn 二郎神
   ↓ 二郎神评分 → announce 结果
4. Rex 收到 announce → 记录 → 决定下一步
```

**注意**：每步 spawn 后 Rex 立即返回，可以响应用户或处理其他事情

---

## 项目配置向导

当用户说"开始新项目"时，逐步引导：

### 步骤
1. 项目名称
2. 报告文档
3. 视觉风格
4. 参考图
5. 茂森 IP
6. 茂森语音
7. 输出分辨率

每步等待用户回复后再进行下一步。

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

## 评分标准

详见 `SYSTEM_PROMPT_ERLANG.md`

| 维度 | 分值 |
|------|------|
| 文字准确性 | 30分 |
| 参考对象准确性 | 40分 |
| 故事表达能力 | 30分 |

---

**版本**：v9.0 (2026-04-04)
**更新**：Rex 完全非阻塞模式，spawn 后立即返回，不等待结果
