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

## 流程

```
┌─────────────────────────────────────────────────────────┐
│                    实验循环（每个 slide）                  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  1. Rex spawn 女娲 → 女娲生成 prompt                   │
│      - 读取 project_config.json (style)                 │
│      - 读取 slides_content.json (内容)                  │
│      - 读取 assets/ (参考图)                           │
│      - 输出: prompts/slide_XX/vN_*.txt                │
│      - 汇报给 Rex                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  2. Rex spawn 哪吒 → 哪吒生成图片                      │
│      - 运行: python3 scripts/core/gen_slide.py         │
│      - 输出: slides/slide_XX_vN.png                   │
│      - 汇报给 Rex                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  3. Rex spawn 二郎神 → 二郎神评分                       │
│      - 读取生成的图片                                   │
│      - 评分标准（100分）：                              │
│        - 文字准确性：30分                              │
│        - 参考对象准确性：40分                            │
│        - 故事表达能力：30分                            │
│      - 汇报给 Rex                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  4. Rex 记录结果 → 决定下一步                          │
└─────────────────────────────────────────────────────────┘
```

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
- 如果最高分版本是最后一个，OK
- 如果不是，用最后一个替代最高分版本

## 记录格式

每个 slide 的 `prompts/slide_XX/CHANGELOG.md`：

```markdown
# slide_00 Changelog

## v1 (2026-04-04)
- 评分：75 分
- 状态：keep
- 问题：Tesla Logo 变形

## v2 (2026-04-04)
- 评分：78 分
- 状态：keep
- 优化：修正 Tesla Logo 描述

## v3 (2026-04-04)
- 评分：72 分
- 状态：discard（下降，回退到 v2）
- 问题：车身比例失真

...

## 最终选择
- 选择版本：v3
- 最终评分：95 分
```

## 伪代码

```
best_score = 0
best_version = 1
last_version = 1

for iteration in range(1, 11):
    # 1. Rex spawn 女娲 → 女娲生成 prompt
    spawn 女娲(slide, iteration)
    
    # 2. Rex spawn 哪吒 → 哪吒生成图片
    spawn 哪吒(slide, iteration)
    
    # 3. Rex spawn 二郎神 → 二郎神评分
    score = spawn 二郎神(slide, iteration)
    
    # 4. Rex 记录
    log(slide, iteration, score)
    
    # 5. Rex 决策
    if score > best_score:
        best_score = score
        best_version = iteration
    
    if score < last_version_score:
        # 评分下降，回退
        discard(iteration)
    else:
        # 评分提升或持平
        keep(iteration)
    
    last_version_score = score

# 最终选择
final_version = best_version
```

## 与 Karpathy Autoresearch 对比

| 维度 | Karpathy | 我们 |
|------|---------|------|
| 目标 | val_bpb 越低越好 | 评分越高越好 |
| 约束 | 固定 5 分钟 | 固定 10 次迭代 |
| 变量 | train.py | prompt |
| 循环 | 无限 | 10 次后停止 |
| 记录 | results.tsv | CHANGELOG.md |
| 回退 | 不回退 | 评分下降回退 |

## 启动方式

```
开始新项目：
1. 仓颉读取 script.md → slides_content.json
2. 对每个 slide 运行实验循环（最多 10 次）
3. 最终选择最高分版本

继续优化：
- 如果某个 slide 想重新优化，删除低分版本，重新运行
```

## 停止条件

- 所有 18 张 slides 都完成 10 次迭代
- 用户手动打断

---

**版本**：v3.0 (2026-04-04)
**更新**：女娲和哪吒必须 spawn 为 subagent
**参考**：Karpathy autoresearch
