#!/usr/bin/env python3
"""
生成 slide_00 图片
"""
import sys
sys.path.append('/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts')

from comfyui_api import ComfyUIQwenImageAPI

# 读取 prompt (v3 版本)
with open('prompts/slide_00_positive_v3.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

print("="*60)
print("生成 slide_00 图片")
print("="*60)
print(f"Prompt:\n{prompt}\n")

# 初始化 API
api = ComfyUIQwenImageAPI("http://100.111.221.7:8188")

# 生成图片（Lightning 模式，快速）
result = api.generate_image(
    prompt_text=prompt,
    negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲",
    width=1664,
    height=928,
    seed=None,  # 随机种子
    use_lightning=True,  # Lightning 模式（4 步）
    filename_prefix="slide_00_v3"
)

print(f"\n结果：{result}")
