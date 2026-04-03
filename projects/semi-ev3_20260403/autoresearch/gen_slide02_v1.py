#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

API_URL = "http://100.111.221.7:8188"

with open('ComfyUI/Qwen-Image-2512_ComfyUI.json', 'r') as f:
    workflow = json.load(f)

# 读取 slide_02 提示词
with open('projects/semi-ev3_20260403/prompts/slide_02.txt', 'r') as f:
    positive_prompt = f.read()

negative_prompt = """AI generated, digital rendering, 3D render, photorealistic, smooth rendering, hyperrealistic

低画质，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节

银色车身，灰色涂装，传统卡车造型

文字错别字，文字乱码，模糊文字，奇怪符号

烟雾特效，营销风格，商业封面风

轮毂AI感，零件边界模糊"""

for node_id, node in workflow.items():
    if node.get('class_type') == 'CLIPTextEncode':
        if 'text' in node.get('inputs', {}):
            node['inputs']['text'] = positive_prompt
    elif node.get('class_type') == 'EmptySD3LatentImage':
        node['inputs']['width'] = 1280
        node['inputs']['height'] = 800
    elif node.get('class_type') == 'PrimitiveBoolean':
        node['inputs']['value'] = False

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
                        with open('projects/semi-ev3_20260403/slides/slide_02_v1.png', 'wb') as f:
                            f.write(img_response.content)
                        print(f"Downloaded: {filename}")
            break
        time.sleep(2)
    else:
        print("Timeout")
else:
    print("Failed")
