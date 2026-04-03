#!/usr/bin/env python3
import requests, json, time, random, os

os.chdir('/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403')

with open('prompts/slide_01_positive.txt', 'r', encoding='utf-8') as f:
    positive = f.read().strip()
with open('prompts/slide_01_negative.txt', 'r', encoding='utf-8') as f:
    negative = f.read().strip()

seed = random.randint(0, 2**32-1)
print(f"🎲 Seed: {seed}")
print(f"✅ 正向提示词长度：{len(positive)}")
print(f"✅ 负向提示词长度：{len(negative)}")

prompt = {
    "3": {"inputs": {"seed": seed, "steps": 50, "cfg": 4, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
    "4": {"inputs": {"ckpt_name": "qwen_image_2512_fp8_e4m3fn.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "5": {"inputs": {"width": 1280, "height": 800, "batch_size": 1}, "class_type": "EmptyLatentImage"},
    "6": {"inputs": {"text": positive, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "7": {"inputs": {"text": negative, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
    "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
    "9": {"inputs": {"filename_prefix": "slide_01", "images": ["8", 0]}, "class_type": "SaveImage"}
}

r = requests.post('http://100.111.221.7:8188/prompt', json=prompt)
pid = r.json().get('prompt_id', 'unknown')
print(f"✅ Prompt ID: {pid}")
print(f"⏳ 等待生成完成...")

start = time.time()
while time.time() - start < 300:
    h = requests.get(f'http://100.111.221.7:8188/history/{pid}').json()
    if pid in h:
        imgs = h[pid].get('outputs', {}).get('9', {}).get('images', [])
        if imgs:
            fn = imgs[0].get('filename', '')
            print(f"📥 下载：{fn}")
            img = requests.get(f'http://100.111.221.7:8188/view?filename={fn}')
            with open('slides/slide_01.png', 'wb') as f:
                f.write(img.content)
            print(f"✅ 完成！耗时 {time.time()-start:.1f}s")
            print(f"📁 保存到：slides/slide_01.png")
            break
    time.sleep(2)
