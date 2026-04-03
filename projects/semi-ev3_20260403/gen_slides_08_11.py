#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts/core')
from gen_slide import generate_image

PROJECT = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403"
API_URL = "http://100.111.221.7:8188"

slides = ["08", "09", "10", "11"]

for slide_num in slides:
    positive_file = f"{PROJECT}/prompts/slide_{slide_num}_positive.txt"
    negative_file = f"{PROJECT}/prompts/slide_{slide_num}_negative.txt"
    output_file = f"{PROJECT}/slides/slide_{slide_num}.png"
    
    with open(positive_file, 'r', encoding='utf-8') as f:
        positive_prompt = f.read().strip()
    with open(negative_file, 'r', encoding='utf-8') as f:
        negative_prompt = f.read().strip()
    
    print(f"\n=== Generating slide_{slide_num} ===")
    success = generate_image(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        output_path=output_file,
        width=1664,
        height=928,
        api_url=API_URL
    )
    if success:
        print(f"✅ slide_{slide_num} 完成")
    else:
        print(f"❌ slide_{slide_num} 失败")
