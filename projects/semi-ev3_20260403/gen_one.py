#!/usr/bin/env python3
"""Generate a single slide image via ComfyUI API"""
import os
import sys
import json
import random
import time
import requests
from pathlib import Path

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = Path("/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json")

def generate_slide(positive_prompt, negative_prompt, output_path, width=1664, height=928):
    seed = random.randint(0, 2**32 - 1)
    print(f"  Seed: {seed}", flush=True)
    
    with open(WORKFLOW_PATH, 'r') as f:
        workflow = json.load(f)
    
    for node_id, node in workflow.items():
        if node.get('class_type') == 'CLIPTextEncode':
            inputs = node.get('inputs', {})
            if 'text' in inputs:
                if 'negative' in node_id.lower() or 'neg' in node_id.lower():
                    inputs['text'] = negative_prompt
                else:
                    inputs['text'] = positive_prompt
        elif node.get('class_type') == 'EmptySD3LatentImage':
            node['inputs']['width'] = width
            node['inputs']['height'] = height
            node['inputs']['seed'] = seed
        elif node.get('class_type') == 'PrimitiveBoolean':
            node['inputs']['value'] = False
    
    data = {"prompt": workflow}
    response = requests.post(f"{API_URL}/prompt", json=data, timeout=30)
    result = response.json()
    task_id = result.get('prompt_id')
    
    if not task_id:
        print(f"  ✗ 提交失败：{result}", flush=True)
        return False
    
    print(f"  Task ID: {task_id}", flush=True)
    
    max_wait = 1800
    start_time = time.time()
    while time.time() - start_time < max_wait:
        history = requests.get(f"{API_URL}/history/{task_id}", timeout=10).json()
        if task_id in history:
            for node_id, node_output in history[task_id].get('outputs', {}).items():
                if 'images' in node_output:
                    for img in node_output['images']:
                        filename = img['filename']
                        img_response = requests.get(f"{API_URL}/view?filename={filename}", timeout=30)
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"  ✓ 保存到: {output_path}", flush=True)
            return True
        time.sleep(2)
    
    print(f"  ✗ 超时", flush=True)
    return False

if __name__ == "__main__":
    slide_num = sys.argv[1] if len(sys.argv) > 1 else "08"
    project = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403"
    
    positive_file = f"{project}/prompts/slide_{slide_num}_positive.txt"
    negative_file = f"{project}/prompts/slide_{slide_num}_negative.txt"
    output_file = f"{project}/slides/slide_{slide_num}.png"
    
    print(f"读取正向提示词: {positive_file}", flush=True)
    with open(positive_file, 'r', encoding='utf-8') as f:
        positive_prompt = f.read().strip()
    
    print(f"读取负向提示词: {negative_file}", flush=True)
    with open(negative_file, 'r', encoding='utf-8') as f:
        negative_prompt = f.read().strip()
    
    print(f"\n生成 slide_{slide_num}...", flush=True)
    success = generate_slide(positive_prompt, negative_prompt, output_file)
    
    if success:
        print(f"✅ slide_{slide_num} 完成!", flush=True)
    else:
        print(f"❌ slide_{slide_num} 失败!", flush=True)
        sys.exit(1)
