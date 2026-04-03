#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 slide_01 图片
"""
import requests
import json
import time
import random
import os

# 读取提示词
with open('prompts/slide_01_positive.txt', 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

with open('prompts/slide_01_negative.txt', 'r', encoding='utf-8') as f:
    negative_prompt = f.read().strip()

print("=" * 60)
print("生成 slide_01 图片")
print("=" * 60)

# 随机 seed
seed = random.randint(0, 2**32 - 1)
print(f"🎲 Seed: {seed}")
print(f"✅ 正向提示词长度：{len(positive_prompt)}")
print(f"✅ 负向提示词长度：{len(negative_prompt)}")
print(f"📐 分辨率：1280x800, Steps: 50, CFG: 4")
print(f"🚀 发送请求到 ComfyUI...")

# ComfyUI prompt
prompt = {
    "3": {
        "inputs": {
            "seed": seed,
            "steps": 50,
            "cfg": 4,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler",
        "_meta": {"title": "KSampler"}
    },
    "4": {
        "inputs": {
            "ckpt_name": "qwen_image_2512_fp8_e4m3fn.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {"title": "Load Checkpoint"}
    },
    "5": {
        "inputs": {
            "width": 1280,
            "height": 800,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {"title": "Empty Latent Image"}
    },
    "6": {
        "inputs": {
            "text": positive_prompt,
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title":CLIP Text Encode (Positive)"}
    },
    "7": {
        "inputs": {
            "text": negative_prompt,
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "CLIP Text Encode (Negative)"}
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode",
        "_meta": {"title": "VAE Decode"}
    },
    "9": {
        "inputs": {
            "filename_prefix": "slide_01",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Image"}
    }
}

# 发送请求
response = requests.post(
    'http://100.111.221.7:8188/prompt',
    json=prompt
)

result = response.json()
prompt_id = result.get('prompt_id', 'unknown')
print(f"✅ Prompt ID: {prompt_id}")
print(f"⏳ 等待生成完成...")

# 等待生成
start_time = time.time()
max_wait = 300  # 最多等待 5 分钟

while time.time() - start_time < max_wait:
    history = requests.get(f'http://100.111.221.7:8188/history/{prompt_id}')
    history_data = history.json()
    
    if prompt_id in history_data:
        outputs = history_data[prompt_id].get('outputs', {})
        images = outputs.get('9', {}).get('images', [])
        
        if images:
            filename = images[0].get('filename', '')
            print(f"📥 下载图片：{filename}")
            
            # 下载图片
            img_response = requests.get(f'http://100.111.221.7:8188/view?filename={filename}')
            elapsed = time.time() - start_time
            
            # 保存图片
            with open('slides/slide_01.png', 'wb') as f:
                f.write(img_response.content)
            
            print(f"✅ 完成！耗时 {elapsed:.1f}s")
            print(f"📁 保存到：slides/slide_01.png")
            
            result_info = {
                'status': 'success',
                'filename': 'slide_01.png',
                'prompt_id': prompt_id,
                'seed': seed,
                'elapsed': elapsed
            }
            print(f"\n📊 结果：{json.dumps(result_info, indent=2, ensure_ascii=False)}")
            break
        
    time.sleep(2)
else:
    print("❌ 超时！生成失败")
