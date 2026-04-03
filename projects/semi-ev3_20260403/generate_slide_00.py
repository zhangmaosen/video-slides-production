#!/usr/bin/env python3
"""
生成 slide_00 图片
使用 Qwen-Image-2512 ComfyUI 工作流
"""
import json
import urllib.request
import urllib.error
import os
import time
import random

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"
PROJECT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "slides")

# 读取提示词
with open(os.path.join(PROJECT_DIR, "prompts/slide_00_positive.txt"), "r", encoding="utf-8") as f:
    POSITIVE_PROMPT = f.read().strip()

with open(os.path.join(PROJECT_DIR, "prompts/slide_00_negative.txt"), "r", encoding="utf-8") as f:
    NEGATIVE_PROMPT = f.read().strip()

def generate_slide_00(seed=None, steps=50, cfg=4):
    """生成 slide_00 图片"""
    # 加载 workflow
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # 生成随机 seed
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    print(f"🎲 Seed: {seed}")
    print(f"✅ 正向提示词长度：{len(POSITIVE_PROMPT)}")
    print(f"✅ 负向提示词长度：{len(NEGATIVE_PROMPT)}")

    # 修改 workflow
    workflow["238:227"]["inputs"]["text"] = POSITIVE_PROMPT  # Positive prompt
    workflow["238:228"]["inputs"]["text"] = NEGATIVE_PROMPT  # Negative prompt
    workflow["238:232"]["inputs"]["width"] = 1280
    workflow["238:232"]["inputs"]["height"] = 800
    workflow["238:230"]["inputs"]["seed"] = seed
    workflow["238:224"]["inputs"]["value"] = steps  # Steps
    workflow["238:223"]["inputs"]["value"] = cfg  # CFG
    workflow["60"]["inputs"]["filename_prefix"] = "slide_00"

    print(f"📐 分辨率：1280x800, Steps: {steps}, CFG: {cfg}")

    # 发送到 ComfyUI - 关键：需要包装在 {"prompt": workflow} 中
    print(f"🚀 发送请求到 ComfyUI...")
    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(
        f"{API_URL}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            prompt_id = result.get('prompt_id')
            print(f"✅ Prompt ID: {prompt_id}")

            if not prompt_id:
                return {"status": "error", "error": "No prompt_id returned"}

            # 等待完成
            print(f"⏳ 等待生成完成...")
            max_wait = 900  # 15 分钟超时
            start_time = time.time()

            while time.time() - start_time < max_wait:
                time.sleep(10)
                try:
                    history_req = urllib.request.Request(
                        f"{API_URL}/history/{prompt_id}",
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(history_req, timeout=30) as hist_resp:
                        history = json.loads(hist_resp.read().decode('utf-8'))

                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                for img_info in node_output['images']:
                                    filename = img_info['filename']
                                    subfolder = img_info.get('subfolder', '')

                                    # 下载图片
                                    print(f"📥 下载图片：{filename}")
                                    image_url = f"{API_URL}/view?filename={filename}&subfolder={subfolder}"
                                    with urllib.request.urlopen(image_url, timeout=60) as img_resp:
                                        image_data = img_resp.read()

                                    # 保存
                                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                                    output_path = os.path.join(OUTPUT_DIR, "slide_00_v2.png")
                                    with open(output_path, 'wb') as f:
                                        f.write(image_data)

                                    elapsed = time.time() - start_time
                                    print(f"✅ 完成！耗时 {elapsed:.1f}s")
                                    print(f"📁 保存到：{output_path}")
                                    return {
                                        "status": "success",
                                        "filename": "slide_00_v2.png",
                                        "prompt_id": prompt_id,
                                        "seed": seed,
                                        "elapsed": elapsed
                                    }
                except Exception as e:
                    print(f"  检查状态时出错：{e}, 继续等待...")
                    time.sleep(5)

            return {"status": "error", "error": "Timeout waiting for generation"}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"status": "error", "error": f"HTTP {e.code}: {error_body[:300]}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("="*60)
    print("生成 slide_00 图片")
    print("="*60)
    
    result = generate_slide_00()
    print(f"\n📊 结果：{result}")
