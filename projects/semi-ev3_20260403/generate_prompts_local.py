#!/usr/bin/env python3
"""
本地生成提示词 - 不使用 API，直接应用元模板
"""
import json
import os

# 读取元模板
with open('../META_PROMPT.md', 'r', encoding='utf-8') as f:
    meta_template = f.read()

# 读取 slides 内容
with open('slides_content.json', 'r', encoding='utf-8') as f:
    slides_content = json.load(f)

# 读取项目配置
with open('project_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

style = config['style']

# 创建 prompts 目录
os.makedirs('prompts', exist_ok=True)

# 为每个 slide 生成提示词
for slide_key, slide_data in sorted(slides_content.items()):
    title = slide_data.get('title', '')
    viewpoint = slide_data.get('viewpoint', '')
    script = slide_data.get('script', '')
    background = slide_data.get('background', '')
    
    # 构建用户输入
    user_input = f"""
- 视觉风格：{style}
- 标题：{title}
- 观点：{viewpoint}
- 逐字稿：{script}
- 背景知识：{background}
"""
    
    # 应用元模板
    if "{用户输入}" in meta_template:
        prompt = meta_template.replace("{用户输入}", user_input)
    else:
        prompt = meta_template + f"\n---\n\n# 用户输入\n{user_input}"
    
    # 保存
    output_path = os.path.join('prompts', f"{slide_key}.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"✓ {slide_key}: {title} ({len(prompt)} 字符)")

print(f"\n完成！已生成 {len(slides_content)} 个 prompt 文件")
