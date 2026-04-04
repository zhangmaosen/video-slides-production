# Video Slides Production

视频幻灯片生产技能。

## 核心文档

| 文件 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 主文档，Rex 交互规则和工作流程 |
| [AUTORESEARCH_LOOP.md](AUTORESEARCH_LOOP.md) | Autoresearch 循环流程 |
| [SYSTEM_PROMPT_NVWA.md](SYSTEM_PROMPT_NVWA.md) | 女娲 System Prompt |
| [SYSTEM_PROMPT_CANGJIE.md](SYSTEM_PROMPT_CANGJIE.md) | 仓颉 System Prompt |
| [SYSTEM_PROMPT_ERLANG.md](SYSTEM_PROMPT_ERLANG.md) | 二郎神 System Prompt |

## 核心流程

```
a. 报告文档 → slides_content.json（仓颉）
b. 素材整理（图片、茂森IP）
c. Autoresearch Loop（最多10次迭代）
d. TTS生成
e. FFmpeg视频合成
```

## Autoresearch Loop

每个 slide 最多迭代 10 次，选最高分：
1. Rex spawn 女娲（基于最高分版本生成）
2. Rex spawn 哪吒（生成图片）
3. Rex spawn 二郎神（评分）
4. Rex 记录并决定回退/继续

## 评分标准

详见 `SYSTEM_PROMPT_ERLANG.md`

| 维度 | 分值 |
|------|------|
| 文字准确性 | 30分 |
| 参考对象准确性 | 40分 |
| 故事表达能力 | 30分 |

---

**版本**：v2.0 (2026-04-04)
