# 幻灯片 Autoresearch Loop

## 核心理念

给 AI Agent 一个固定的工作流程，让它自主实验迭代。

**参考：** Karpathy autoresearch - 固定迭代，目标最优

## 角色分工

| 角色 | 职责 | 执行者 |
|------|------|--------|
| **仓颉** | 内容整理（slides_content.json） | Agent |
| **女娲** | 生成和优化 prompt | **Agent（必须 spawn）** |
| **哪吒** | 生成图片 | **Agent（必须 spawn）** |
| **二郎神** | 评分 + 扣分点 | Agent |
| **Rex** | 协调循环、记录、决策 | 人类/Rex |

**Rex 职责：**
1. 协调团队执行 AUTORESEARCH LOOP
2. 记录每次迭代的评分
3. 决策何时回退、何时停止
4. 最终选择最高分版本

**重要：女娲和哪吒必须 spawn 为 subagent，由 Rex 调度执行！**

---

## 核心规则：必须基于最佳版本生成

### 回退机制（关键！）

女娲生成新版本时，**必须基于当前最高分的版本**，而不是上一版本：

```
❌ 错误逻辑：
v4(90分) → 基于v4生成v5 → v5(80分) → 基于v5生成v6（继承v5缺点）

✅ 正确逻辑：
v4(90分) → 基于v4生成v5 → v5(80分) → 回退到v4 → 基于v4+v5反馈生成v6
```

**Rex 必须告诉女娲：**
1. 当前最高分版本是哪个
2. 女娲必须读取最高分版本的 prompt 作为基础
3. 女娲只能应用二郎神的扣分反馈来优化

---

## 女娲职责（必须遵守）

### 输入
1. **参考图** - 必须读取 `assets/` 目录下的参考图，分析特征
2. **slides_content.json** - 当前 slide 的内容
3. **CHANGELOG.md** - 迭代历史，了解之前版本的问题
4. **二郎神反馈** - 上一版本的扣分点和优化建议
5. **Rex 指令** - 告知女娲使用哪个版本作为基础（通常是最高分版本）

### 输出
- `prompts/slide_XX/vN_positive.txt` - 正向提示词
- `prompts/slide_XX/vN_negative.txt` - 负向提示词
- 更新 `CHANGELOG.md`

### 女娲 prompt 模板
```
你是女娲，负责生成图片提示词。

## 任务
1. 读取项目目录下的参考图（assets/），分析特征
2. 读取 slides_content.json 了解当前 slide 内容
3. 读取 CHANGELOG.md 了解迭代历史
4. 读取基础版本（当前最高分版本）的 prompt
5. 根据二郎神的反馈优化 prompt

## Rex 指令
基础版本：v{X}（当前最高分版本，分数：{score}分）

## 参考图路径
{project_path}/assets/

## 输出
写入：
- {project_path}/prompts/slide_{num}/v{version}_positive.txt
- {project_path}/prompts/slide_{num}/v{version}_negative.txt
```

---

## 哪吒职责

### 输入
- 女娲生成的 prompt 文件

### 输出
- `slides/slide_XX_vN.png` - 生成的图片

---

## 二郎神职责（必须遵守）

### 输入
1. **生成的图片** - 待评分的图片
2. **参考图** - 必须读取 `assets/` 目录下的参考图，逐项对比
3. **slides_content.json** - 当前 slide 的内容，用于核对文字

### System Prompt
`SYSTEM_PROMPT_ERLANG.md`

---

## 流程

```
┌─────────────────────────────────────────────────────────┐
│                    实验循环（每个 slide）                  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  1. Rex 查找当前最高分版本                              │
│      读取 CHANGELOG.md，找到最高分版本 X                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  2. Rex spawn 女娲                                     │
│      告诉女娲：基础版本是 vX（最高分）                 │
│      女娲必须读取：                                      │
│      - 参考图（assets/）                              │
│      - slides_content.json                            │
│      - CHANGELOG.md（迭代历史）                       │
│      - 二郎神反馈（上一版本）                          │
│      - 最高分版本 vX 的 prompt                       │
│      → 基于 vX + 二郎神反馈生成 vN                    │
│      → 汇报给 Rex                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  3. Rex spawn 哪吒                                    │
│      → 生成图片 → 汇报给 Rex                           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  4. Rex spawn 二郎神                                   │
│      二郎神必须读取：                                   │
│      - 参考图（assets/）逐项对比                      │
│      - 生成的图片                                      │
│      - slides_content.json                            │
│      → 评分 → 汇报给 Rex                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  5. Rex 记录结果 → 更新 CHANGELOG.md                 │
│      → 比较分数，决定下一步（继续/回退/停止）           │
└─────────────────────────────────────────────────────────┘
```

---

## 实验规则

### 1. 固定迭代次数
- **最大迭代 10 次**
- 10 次后强制选择最高分

### 2. 评分越高越好
- 没有 92 分门槛
- 目标：尽可能高的分数

### 3. 回退机制（关键！）
- 如果新版本评分下降 → 回退到历史最高分版本
- 女娲必须基于历史最高分版本来生成新 prompt
- 不能基于分数更低的版本来生成

### 4. 最终选择
- 10 次迭代后，选择评分最高的版本

---

## 记录格式

每个 slide 的 `prompts/slide_XX/CHANGELOG.md`：

```markdown
# slide_00 Changelog

## v1 (2026-04-04)
- 评分：75 分
- 状态：discard
- 问题：Tesla Logo 变形

## v2 (2026-04-04)
- 评分：90 分 ✅ 当前最高
- 状态：keep
- 二郎神反馈：挡风玻璃比例偏大

## v3 (2026-04-04)
- 评分：80 分
- 状态：discard（回退到v2）
- 问题：颜色失真

## v4 (2026-04-04)
- 评分：95 分 ✅ 当前最高
- 状态：keep
- 优化：基于v2 + v3反馈生成

## 最终选择
- 选择版本：v4
- 最终评分：95 分
```

---

## 伪代码

```
best_score = 0
best_version = 1

for iteration in range(1, 11):
    # 1. Rex 查找当前最高分版本
    best_version = get_best_version(CHANGELOG)
    best_score = get_best_score(CHANGELOG)
    
    # 2. Rex spawn 女娲（告诉基础版本）
    spawn 女娲(slide, iteration, base_version=best_version)
    
    # 3. Rex spawn 哪吒
    spawn 哪吒(slide, iteration)
    
    # 4. Rex spawn 二郎神
    score = spawn 二郎神(slide, iteration)
    
    # 5. Rex 记录
    update CHANGELOG(slide, iteration, score, 二郎神反馈)
    
    # 6. Rex 决策
    if score > best_score:
        best_score = score
        best_version = iteration
    
    if score < best_score:
        # 新版本更差，标记为 discard
        discard(iteration)
        # 下一次迭代会回退到 best_version
    else:
        keep(iteration)

final_version = best_version
```

---

**版本**：v5.0 (2026-04-04)
**更新**：关键修复 - 女娲必须基于当前最高分版本生成，不能基于上一版本
