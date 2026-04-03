#!/usr/bin/env python3
"""直接生成幻灯片图片"""
import json
import urllib.request
import urllib.error
import os
import sys
import time
import random

API_URL = "http://zhang.taileefd9.ts.net:8188"  # Use hostname instead of IP
WORKFLOW_PATH = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"

NEGATIVE_PROMPT = "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲，文字错别字，文字乱码，模糊文字，奇怪符号，AI 字体"

def generate_image(prompt_text, output_path, seed=None, steps=50, cfg=4, width=1664, height=928):
    """生成单张图片"""
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    print(f"  Seed: {seed}, Steps: {steps}, CFG: {cfg}, Size: {width}x{height}")
    print(f"  Prompt 长度: {len(prompt_text)} 字符")

    workflow["238:227"]["inputs"]["text"] = prompt_text
    workflow["238:228"]["inputs"]["text"] = NEGATIVE_PROMPT
    workflow["238:232"]["inputs"]["width"] = width
    workflow["238:232"]["inputs"]["height"] = height
    workflow["238:230"]["inputs"]["seed"] = seed
    workflow["238:224"]["inputs"]["value"] = steps
    workflow["238:223"]["inputs"]["value"] = cfg

    print(f"  发送请求到 ComfyUI...")
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
            print(f"  Prompt ID: {prompt_id}")

            if not prompt_id:
                return {"status": "error", "error": "No prompt_id returned"}

            print(f"  等待生成完成...")
            max_wait = 900
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

                                    print(f"  下载图片: {filename}")
                                    image_url = f"{API_URL}/view?filename={filename}&subfolder={subfolder}"
                                    with urllib.request.urlopen(image_url, timeout=60) as img_resp:
                                        image_data = img_resp.read()

                                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                                    with open(output_path, 'wb') as f:
                                        f.write(image_data)

                                    elapsed = time.time() - start_time
                                    print(f"  完成！耗时 {elapsed:.1f}s -> {output_path}")
                                    return {
                                        "status": "success",
                                        "filename": output_path,
                                        "prompt_id": prompt_id,
                                        "seed": seed,
                                        "elapsed": elapsed
                                    }
                except Exception as e:
                    print(f"  检查状态时出错: {e}, 继续等待...")
                    time.sleep(5)

            return {"status": "error", "error": "Timeout waiting for generation"}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return {"status": "error", "error": f"HTTP {e.code}: {error_body[:300]}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 gen_simple.py <prompt_file> <output_file>")
        sys.exit(1)

    prompt_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read()

    print("=" * 60)
    print("生成图片")
    print("=" * 60)
    print(f"Prompt 文件: {prompt_file}")
    print(f"输出文件: {output_file}")

    result = generate_image(prompt_text, output_file)
    print(f"\n结果: {result}")
