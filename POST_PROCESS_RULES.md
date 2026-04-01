# 图片提示词后处理规则 (POST_PROCESS_RULES)

## 项目信息
- **项目名称**：特斯拉 Semi 视频
- **版本**：v1.0
- **更新时间**：2026-04-01

---

## 条件追加规则

### 规则 1：Tesla Semi 特征追加

**触发条件**：原始内容包含 "semi" 或 "Semi"（不区分大小写）

**追加内容**：
```
重要：如果画面涉及特斯拉 Semi 卡车，必须严格遵循以下视觉特征描述：
全封闭车身前脸（无传统进气格栅），
全宽贯穿式水平 LED 车头灯带，
细长车头大灯无缝集成在灯带两侧，
更小的环绕挡风玻璃，
圆润光滑的车顶线条，
一体式封闭前保险杠。
```

**优先级**：高

**说明**：确保 Tesla Semi 的标志性设计元素在所有相关画面中保持一致。

---

### 规则 2：燃油卡车对比元素

**触发条件**：原始内容包含 "柴油"、"燃油"、"传统卡车" 等关键词

**追加内容**：
```
重要：传统燃油卡车的视觉特征：
臃肿的发动机舱设计，
宽大的进气格栅，
复杂的机械结构外露，
排气管冒出黑烟，
车身涂装斑驳褪色，
生锈的铆钉和螺栓细节。
```

**优先级**：中

**说明**：强化新旧技术对比的视觉张力。

---

### 规则 3：充电场景元素

**触发条件**：原始内容包含 "充电"、"MCS"、"兆瓦" 等关键词

**追加内容**：
```
重要：充电场景的视觉细节：
粗壮的充电线缆（可见编织屏蔽层），
重型连接器接口，
蓝色能量光晕从接触点散发，
充电桩数字显示屏，
地面充电标识线。
```

**优先级**：中

**说明**：增强充电场景的技术感和真实感。

---

### 规则 4：司机体验场景

**触发条件**：原始内容包含 "司机"、"驾驶员"、"驾驶" 等关键词

**追加内容**：
```
重要：司机场景的视觉细节：
放松的坐姿（无离合器踏板），
双手轻握方向盘，
数字仪表盘显示，
全景玻璃驾驶舱，
人体工学座椅，
降噪耳机（可选）。
```

**优先级**：低

**说明**：突出电动卡车的驾驶体验优势。

---

## 后处理流程

```python
def post_process_prompt(ai_generated_prompt, original_content):
    """
    对 AI 生成的提示词进行后处理，根据条件追加规则
    
    Args:
        ai_generated_prompt: AI 生成的原始提示词
        original_content: 用户的原始输入内容（用于判断触发条件）
    
    Returns:
        final_prompt: 后处理后的最终提示词
    """
    final_prompt = ai_generated_prompt.strip()
    content_lower = original_content.lower()
    
    # 规则 1：Tesla Semi 特征
    if "semi" in content_lower:
        final_prompt += "\n\n重要：如果画面涉及特斯拉 Semi 卡车，必须严格遵循以下视觉特征描述：\n"
        final_prompt += "全封闭车身前脸（无传统进气格栅），\n"
        final_prompt += "全宽贯穿式水平 LED 车头灯带，\n"
        final_prompt += "细长车头大灯无缝集成在灯带两侧，\n"
        final_prompt += "更小的环绕挡风玻璃，\n"
        final_prompt += "圆润光滑的车顶线条，\n"
        final_prompt += "一体式封闭前保险杠。"
    
    # 规则 2：燃油卡车对比
    if any(keyword in content_lower for keyword in ["柴油", "燃油", "传统卡车"]):
        final_prompt += "\n\n重要：传统燃油卡车的视觉特征：\n"
        final_prompt += "臃肿的发动机舱设计，\n"
        final_prompt += "宽大的进气格栅，\n"
        final_prompt += "复杂的机械结构外露，\n"
        final_prompt += "排气管冒出黑烟，\n"
        final_prompt += "车身涂装斑驳褪色，\n"
        final_prompt += "生锈的铆钉和螺栓细节。"
    
    # 规则 3：充电场景
    if any(keyword in content_lower for keyword in ["充电", "mcs", "兆瓦"]):
        final_prompt += "\n\n重要：充电场景的视觉细节：\n"
        final_prompt += "粗壮的充电线缆（可见编织屏蔽层），\n"
        final_prompt += "重型连接器接口，\n"
        final_prompt += "蓝色能量光晕从接触点散发，\n"
        final_prompt += "充电桩数字显示屏，\n"
        final_prompt += "地面充电标识线。"
    
    # 规则 4：司机体验
    if any(keyword in content_lower for keyword in ["司机", "驾驶员", "驾驶"]):
        final_prompt += "\n\n重要：司机场景的视觉细节：\n"
        final_prompt += "放松的坐姿（无离合器踏板），\n"
        final_prompt += "双手轻握方向盘，\n"
        final_prompt += "数字仪表盘显示，\n"
        final_prompt += "全景玻璃驾驶舱，\n"
        final_prompt += "人体工学座椅，\n"
        final_prompt += "降噪耳机（可选）。"
    
    return final_prompt
```

---

## 使用方式

**在生成脚本中调用**：
```python
# 1. AI 生成提示词
ai_prompt = generate_with_meta_template(style, content)

# 2. 后处理
final_prompt = post_process_prompt(ai_prompt, content)

# 3. 保存或输出
save_prompt(final_prompt)
```

---

## 扩展指南

**添加新规则**：
1. 定义触发条件（关键词匹配）
2. 编写追加内容（中文描述）
3. 设置优先级（高/中/低）
4. 更新后处理函数

**规则优先级**：
- **高**：核心产品特征（如 Tesla Semi 设计）
- **中**：场景关键元素（如充电细节）
- **低**：辅助性细节（如司机配饰）

---

**版本**：v1.0 (2026-04-01)  
**项目**：特斯拉 Semi 视频  
**文件位置**：`skills/video-slides-production/POST_PROCESS_RULES.md`
