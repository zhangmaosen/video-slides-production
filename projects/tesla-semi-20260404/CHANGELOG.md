# CHANGELOG - Tesla Semi

---

## slide_01

### v4 (2026-04-04)

**评分**：待二郎神评分
**来源**：v3 (92分) + 二郎神反馈

**二郎神 v3 反馈**：
- 优点：文字满分(30/30)、叙事感强（经济图表对比）、司机姿势正确、情绪表达强
- 小问题：右手手指轻微AI畸形、加油站背景右侧线条凌乱、车轮轮毂轻微扭曲

**改动点**：
- **背景简化**：`simple clean gas station background on the right side, uncluttered` 替代 `comic book illustration with bold outlines` 避免右侧线条凌乱
- **车轮简化**：`Clean wheel rims on the truck, simple spoke details` 替代 `clean background` 中的模糊描述，避免轮毂扭曲
- **手部负向追加**：追加 `distorted fingers, blurry hand details`
- **车轮负向追加**：追加 `distorted wheel rims, messy wheel details`
- **负向精简**：合并重复项（deformed hands + extra fingers 保留，更明确）

**v4 prompt（545字符）**：
```
Hand-drawn comic scene of a truck driver sitting at the cab door of a diesel heavy-duty semi-truck, feet firmly on the ground, one hand resting on the door frame, exhausted expression with dark circles. Giant fuel price sign behind the truck showing "$0.80/mi". Old dirty diesel truck with black exhaust smoke. Simple clean gas station background on the right side, uncluttered. Clean wheel rims on the truck, simple spoke details. Warm dusty highway rest stop atmosphere. Bold outlines, exaggerated expressions, clean simple background. Bold text "没选择" at top left in large white bold font with black shadow, text "$0.80/mi" at bottom right in yellow. Hand-drawn comic, manhua style, 16:9.
```

**v4 负向（441字符）**：
```
low resolution, blurry, deformed, oversaturated, wax-like skin, AI artifacts, messy composition, distorted text, wrong characters, watermark, distorted cab structure, messy grille, unclear body structure, deformed hands, extra fingers, distorted fingers, blurry hand details, floating wheels, broken wheel spokes, distorted wheel rims, messy wheel details, distorted vehicle proportions, cluttered background lines, messy background details
```

### v3 (2026-04-04)

**二郎神评分**：92分
**主要问题**：右手手指轻微AI畸形、加油站背景右侧线条凌乱、车轮轮毂轻微扭曲

---

# CHANGELOG - Tesla Semi slide_00

## v2 (2026-04-04)

**评分**：待二郎神评分
**来源**：v1 (86分) + 二郎神反馈

### 改动点
- **LED灯带**：从"continuous LED bar across the nose"改为"two separate slim horizontal white LED strips on the upper edge of the nose with a gap in the center"（分体细长式，与参考图一致）
- **负向提示词**：追加"continuous LED bar across nose, single unbroken LED strip"，明确禁止画成贯穿式

### v2 prompt（746字符）
```
Hand-drawn comic scene, center of frame features an oversized cartoon Tesla Semi truck, white aerodynamic bullet-shaped cab, two separate slim horizontal white LED strips on the upper edge of the nose with a gap in the center, massive wraparound windshield, tall roof fairing, standing on a highway road. To the left, a chibi big-head cartoon character with thick black messy hair, heavy black eyebrows, wearing a white t-shirt, hands on hips, giving a thumbs-up with a smug grin, standing confidently beside the truck. Simple speed lines and comic dot background, dynamic action vibe. Bold text "特斯拉 Semi" at top center, smaller text "重卡江湖大结局" at bottom center. Hand-drawn comic illustration, thick black outlines, cartoon style, halftone dots.
```

---

## v1 (2026-04-04)

**二郎神评分**：86分
**主要问题**：
- LED灯带是贯穿式（参考图是分体细长式）→ 扣分
- 其他外观特征正确

### v1 prompt（682字符）
```
Hand-drawn comic scene, center of frame features an oversized cartoon Tesla Semi truck, white aerodynamic bullet-shaped cab, slim horizontal white LED light bar across the nose, massive wraparound windshield, tall roof fairing, standing on a highway road. To the left, a chibi big-head cartoon character with thick black messy hair, heavy black eyebrows, wearing a white t-shirt, hands on hips, giving a thumbs-up with a smug grin, standing confidently beside the truck. Simple speed lines and comic dot background, dynamic action vibe. Bold text "特斯拉 Semi" at top center, smaller text "重卡江湖大结局" at bottom center. Hand-drawn comic illustration, thick black outlines, cartoon style, halftone dots.
```
