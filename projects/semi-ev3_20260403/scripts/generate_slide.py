#!/usr/bin/env python3
"""
Tesla Semi 幻灯片图片生成脚本
使用 Qwen-Image-2512 ComfyUI 工作流生成图片
"""
import json
import urllib.request
import urllib.error
import os
import sys
import time
import random

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"
OUTPUT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403/slides"

NEGATIVE_PROMPT = """低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲，文字错别字，文字乱码，模糊文字，奇怪符号，AI 字体"""

def generate_image(slide_num, prompt_text, output_filename, seed=None, steps=50, cfg=4):
    """生成单张图片"""
    # 加载 workflow
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # 生成随机 seed
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    # 修改 workflow
    workflow["238:227"]["inputs"]["text"] = prompt_text  # Positive prompt
    workflow["238:228"]["inputs"]["text"] = NEGATIVE_PROMPT  # Negative prompt
    workflow["238:232"]["inputs"]["width"] = 1664
    workflow["238:232"]["inputs"]["height"] = 928
    workflow["238:230"]["inputs"]["seed"] = seed
    workflow["238:224"]["inputs"]["value"] = steps  # Steps
    workflow["238:223"]["inputs"]["value"] = cfg  # CFG

    print(f"  Seed: {seed}, Steps: {steps}, CFG: {cfg}, Size: 1664x928")

    # 发送到 ComfyUI
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

            # 等待完成
            print(f"  等待生成完成...")
            max_wait = 600  # 10 分钟超时
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
                                    print(f"  下载图片: {filename}")
                                    image_url = f"{API_URL}/view?filename={filename}&subfolder={subfolder}"
                                    with urllib.request.urlopen(image_url, timeout=60) as img_resp:
                                        image_data = img_resp.read()

                                    # 保存
                                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                                    output_path = os.path.join(OUTPUT_DIR, output_filename)
                                    with open(output_path, 'wb') as f:
                                        f.write(image_data)

                                    elapsed = time.time() - start_time
                                    print(f"  ✓ 完成！耗时 {elapsed:.1f}s -> {output_path}")
                                    return {
                                        "status": "success",
                                        "filename": output_filename,
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
        print("用法: python3 generate_slide.py <slide_num> <prompt_file>")
        sys.exit(1)

    slide_num = sys.argv[1]
    prompt_file = sys.argv[2]
    output_file = f"slide_{slide_num}.png"

    # 读取 prompt
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read()

    print(f"="*60)
    print(f"生成 slide_{slide_num} 图片")
    print(f"="*60)
    print(f"Prompt 长度: {len(prompt_text)} 字符")

    result = generate_image(slide_num, prompt_text, output_file)
    print(f"\n结果: {result}")
