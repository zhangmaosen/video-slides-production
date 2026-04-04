# CHANGELOG - slide_01

## v1 (2026-04-04)
- 评分：~82分
- 状态：keep（参考）
- 正向 prompt：手绘漫画，柴油司机在休息站绝望场景，文字"没选择"+"$0.80/mi"
- 问题：车轮结构AI典型瑕疵、加油站细节透视混乱、司机手指细节差

## v2
- 评分：87分
- 状态：参考（已被 v3 超越）
- 正向 prompt：手绘漫画，柴油司机休息站场景，司机疲乏、油价飙升
- 问题：司机身体位置模糊（像挂在车边而非坐在驾驶室）、车头格栅细节和后方车辆形状略显崩坏、手部仍有轻微AI畸形
- 好的地方：情绪张力强、文字准确、车轮透视改善、叙事对比（高油价 vs 低运费）

## v3
- 状态：最新候选
- 正向 prompt：手绘漫画，柴油司机坐在驾驶座门口（双脚落地、一手扶车门），休息站绝望场景，文字"没选择"+"$0.80/mi"
- 字符数：650（符合 400-700 范围）
- 改动：
  - ✅ 司机姿势明确："sitting at the cab door, feet firmly on the ground, one hand resting on the door frame"（解决位置模糊）
  - ✅ 移除对格栅的细节描写（减少AI崩坏）
  - ✅ 简化背景描述（"clean simple background"）
  - ✅ 负向追加：`distorted cab structure, messy grille, unclear body structure, deformed hands, extra fingers`
- 待评分（二郎神）
