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

## 女娲职责（必须遵守）

### 输入
1. **参考图** - 必须读取 `assets/` 目录下的参考图，分析特征
2. **slides_content.json** - 当前 slide 的内容
3. **CHANGELOG.md** - 迭代历史，了解之前版本的问题
4. **二郎神反馈** - 上一版本的扣分点和优化建议

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
4. 根据二郎神的反馈（如果有）优化 prompt

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
│  1. Rex spawn 女娲                                     │
│      女娲必须读取：                                      │
│      - 参考图（assets/）                              │
│      - slides_content.json                            │
│      - CHANGELOG.md（迭代历史）                       │
│      - 二郎神反馈（上一版本）                          │
│      → 生成 prompt → 汇报给 Rex                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  2. Rex spawn 哪吒                                    │
│      → 生成图片 → 汇报给 Rex                           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  3. Rex spawn 二郎神                                   │
│      二郎神必须读取：                                   │
│      - 参考图（assets/）逐项对比                      │
│      - 生成的图片                                      │
│      - slides_content.json                            │
│      → 评分 → 汇报给 Rex                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  4. Rex 记录结果 → 更新 CHANGELOG.md                 │
│      → 决定下一步（继续/回退/停止）                   │
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

### 3. 回退机制
- 如果新版本评分下降 → 回退到上一版本
- 保持历史最高分

### 4. 最终选择
- 10 次迭代后，选择评分最高的版本

---

## 记录格式

每个 slide 的 `prompts/slide_XX/CHANGELOG.md`：

```markdown
# slide_00 Changelog

## v1 (2026-04-04)
- 评分：75 分
- 状态：keep
- 问题：Tesla Logo 变形

## v2 (2026-04-04)
- 评分：82 分
- 状态：keep
- 二郎神反馈：挡风玻璃比例偏大

## v3 (2026-04-04)
- 评分：95 分
- 状态：keep
- 优化：基于二郎神反馈调整

## 最终选择
- 选择版本：v3
- 最终评分：95 分
```

---

## 伪代码

```
best_score = 0
best_version = 1

for iteration in range(1, 11):
    # 1. Rex spawn 女娲
    # 女娲读取：参考图 + slides_content + CHANGELOG + 二郎神反馈
    spawn 女娲(slide, iteration)
    
    # 2. Rex spawn 哪吒
    spawn 哪吒(slide, iteration)
    
    # 3. Rex spawn 二郎神
    # 二郎神读取：参考图逐项对比 + 图片 + slides_content
    score = spawn 二郎神(slide, iteration)
    
    # 4. Rex 记录
    update CHANGELOG(slide, iteration, score,二郎神反馈)
    
    # 5. Rex 决策
    if score > best_score:
        best_score = score
        best_version = iteration
    
    if score < last_score:
        discard(iteration)
    else:
        keep(iteration)
    
    last_score = score

final_version = best_version
```

---

**版本**：v4.0 (2026-04-04)
**更新**：女娲和二郎神必须读取参考图，女娲必须读取二郎神反馈和CHANGELOG
