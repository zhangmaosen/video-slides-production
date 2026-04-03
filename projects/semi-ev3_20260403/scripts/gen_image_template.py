#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用图片生成脚本模板
- 随机 seed
- 动态加载提示词
"""
import requests
import json
import time
import random
import sys
import os

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = "ComfyUI/Qwen-Image-2512_ComfyUI.json"
PROMPT_PATH = "projects/semi-ev3_20260403/prompts/{PROMPT_FILE}"
OUTPUT_PATH = "projects/semi-ev3_20260403/slides/{OUTPUT_FILE}"

# 动态生成随机 seed
RANDOM_SEED = random.randint(0, 2**32 - 1)
print(f"Using random seed: {RANDOM_SEED}")

def generate_image(prompt_file, output_file):
    """生成图片"""
    # 加载 workflow
    with open(WORKFLOW_PATH, 'r') as f:
        workflow = json.load(f)

    # 加载提示词
    prompt_path = PROMPT_PATH.format(PROMPT_FILE=prompt_file)
    with open(prompt_path, 'r') as f:
        positive_prompt = f.read()

    negative_prompt = """AI generated, digital rendering, 3D render, photorealistic, smooth rendering, hyperrealistic

低画质，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节

银色车身，灰色涂装，金属银色涂装，银灰色，metallic silver，silver gray，matte gray，silver metallic，银色车身，灰色涂装，金属银，任何银灰色调

传统卡车造型

文字错别字，文字乱码，模糊文字，奇怪符号

烟雾特效，营销风格，商业封面风

轮毂AI感，零件边界模糊"""

    # 修改 workflow
    for node_id, node in workflow.items():
        if node.get('class_type') == 'CLIPTextEncode':
            if 'text' in node.get('inputs', {}):
                node['inputs']['text'] = positive_prompt
        elif node.get('class_type') == 'EmptySD3LatentImage':
            node['inputs']['width'] = 1280
            node['inputs']['height'] = 800
            node['inputs']['seed'] = RANDOM_SEED
        elif node.get('class_type') == 'PrimitiveBoolean':
            node['inputs']['value'] = False

    # 发送请求
    data = {"prompt": workflow}
    response = requests.post(f"{API_URL}/prompt", json=data)
    result = response.json()
    task_id = result.get('prompt_id')
    print(f"Task ID: {task_id}")

    if task_id:
        max_wait = 300
        start_time = time.time()
        while time.time() - start_time < max_wait:
            history = requests.get(f"{API_URL}/history/{task_id}").json()
            if task_id in history:
                for node_id, node_output in history[task_id].get('outputs', {}).items():
                    if 'images' in node_output:
                        for img in node_output['images']:
                            filename = img['filename']
                            img_response = requests.get(f"{API_URL}/view?filename={filename}")
                            output_path = OUTPUT_PATH.format(OUTPUT_FILE=output_file)
                            with open(output_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"Downloaded: {filename} -> {output_path}")
                break
            time.sleep(2)
        else:
            print("Timeout")
    else:
        print("Failed")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_image.py <prompt_file> <output_file>")
        print("Example: python gen_image.py slide_02_optimized_v2.txt slide_02_v4.png")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_image(prompt_file, output_file)
