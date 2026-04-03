#!/usr/bin/env python3
"""
生成 slide_00 图片 v2 版本
重点修正：
1. 标题必须是"特斯拉 Semi 掀翻燃油卡车"（不是"拆翻"）
2. 添加副标题"一场输不起的商业货运革命"
3. 车轮：前轮封闭式轮毂盖（银灰色），后轮深凹形轮毂（深灰色）
4. 车身：半挂牵引车头造型（不是厢式货车）
"""
import sys
sys.path.append('/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts')

from comfyui_api import ComfyUIQwenImageAPI

# 读取 prompt (v2 版本)
with open('prompts/slide_00_positive_v2.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

with open('prompts/slide_00_negative_v2.txt', 'r', encoding='utf-8') as f:
    negative_prompt = f.read()

print("="*60)
print("生成 slide_00 v2 图片")
print("="*60)
print(f"Prompt:\n{prompt}\n")
print(f"Negative Prompt:\n{negative_prompt}\n")

# 初始化 API
api = ComfyUIQwenImageAPI("http://100.111.221.7:8188")

# 生成图片（Lightning 模式，快速）
result = api.generate_image(
    prompt_text=prompt,
    negative_prompt=negative_prompt,
    width=1664,
    height=928,
    seed=None,  # 随机种子
    use_lightning=True,  # Lightning 模式（4 步）
    filename_prefix="slide_00_v2"
)

print(f"\n结果：{result}")
