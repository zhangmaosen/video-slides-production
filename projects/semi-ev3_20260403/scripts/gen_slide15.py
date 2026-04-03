#!/usr/bin/env python3
"""生成 slide_15 图片"""
import json
import urllib.request
import urllib.error
import os
import time
import random

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"
OUTPUT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403/slides"

NEGATIVE_PROMPT = """低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲，文字错别字，文字乱码，模糊文字，奇怪符号，AI 字体，英文文字，错误数字，混乱排版"""

PROMPT = """混子说手绘 + 硬核工程拆解爆炸图风格，线条粗细变化，诙谐严肃混合，技术细节清晰，结构透视感强，舞台感构图。画面采用舞台感构图，背景是简洁的深色渐变舞台。

画面中央是一张欧洲地图的简化轮廓，以冷蓝色线条勾勒，中央区域被点亮代表已覆盖路网，呈现 50% 路网覆盖的效果。地图上方有高压电塔和充电站的图标标志，能量以蓝色光线连接各充电站。

画面左下角是一辆特斯拉 Semi 电动半挂重型卡车，车身哑光黑色，细长贯穿式 LED 前灯带发出冷冽蓝光，正在一个巨大的兆瓦充电站充电，充电桩屏幕显示 2800kW 的高功率数据。充电桩周围能量四射，蓝白色光芒强烈。

右上角显示 2027 年底 的时间节点，数字醒目，标注强制要求。画面下方显示 2800kW 的数字，以荧光绿大字体呈现，配合深色半透明背景框。欧洲地图外侧标注 已覆盖 50% 路网 的字样。

"欧洲 AFIR" 位于画面顶部居中位置，白色无衬线粗体字体，带有微弱发光效果。"2027" 位于右上角醒目位置。"50%" 位于地图覆盖区域中心，荧光绿数字。"2800kW" 位于左下角充电桩屏幕位置，荧光绿大字体。"""

def generate_image(prompt_text, output_filename, seed=None, steps=50, cfg=4):
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    workflow["238:227"]["inputs"]["text"] = prompt_text
    workflow["238:228"]["inputs"]["text"] = NEGATIVE_PROMPT
    workflow["238:232"]["inputs"]["width"] = 1664
    workflow["238:232"]["inputs"]["height"] = 928
    workflow["238:230"]["inputs"]["seed"] = seed
    workflow["238:224"]["inputs"]["value"] = steps
    workflow["238:223"]["inputs"]["value"] = cfg

    print(f"  Seed: {seed}, Steps: {steps}, CFG: {cfg}, Size: 1664x928")

    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(f"{API_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})

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
                    history_req = urllib.request.Request(f"{API_URL}/history/{prompt_id}", headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(history_req, timeout=30) as hist_resp:
                        history = json.loads(hist_resp.read().decode('utf-8'))
                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})
                        for node_id, node_output in outputs.items():
                            if 'images' in node_output:
                                for img_info in node_output['images']:
                                    filename = img_info['filename']
                                    subfolder = img_info.get('subfolder', '')
                                    image_url = f"{API_URL}/view?filename={filename}&subfolder={subfolder}"
                                    with urllib.request.urlopen(image_url, timeout=60) as img_resp:
                                        image_data = img_resp.read()
                                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                                    output_path = os.path.join(OUTPUT_DIR, output_filename)
                                    with open(output_path, 'wb') as f:
                                        f.write(image_data)
                                    elapsed = time.time() - start_time
                                    print(f"  完成！耗时 {elapsed:.1f}s -> {output_path}")
                                    return {"status": "success", "filename": output_filename, "prompt_id": prompt_id, "seed": seed, "elapsed": elapsed}
                except Exception as e:
                    print(f"  检查状态时出错: {e}, 继续等待...")
                    time.sleep(5)
            return {"status": "error", "error": "Timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    output_file = "slide_15.png"
    print("="*60)
    print("生成 slide_15 图片")
    print("="*60)
    result = generate_image(PROMPT, output_file)
    print(f"\n结果: {result}")
