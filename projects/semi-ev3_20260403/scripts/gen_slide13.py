#!/usr/bin/env python3
"""生成 slide_13 图片"""
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

PROMPT = """混子说手绘 + 硬核工程拆解爆炸图风格，线条粗细变化，诙谐严肃混合，技术细节清晰，结构透视感强，舞台感构图。画面采用舞台感构图，中央是一块巨大的磷酸铁锂 LFP 电池包爆炸拆解图，所有零件呈放射状展开，能量以冷蓝色光纹从电芯向外扩散。背景是简洁的深色渐变舞台。

画面左侧是一辆特斯拉 Semi 电动半挂重型卡车，车身哑光黑色，细长贯穿式 LED 前灯带发出冷冽蓝光，科技蓝色光纹在车身表面流动。电池包从车身底部展开成爆炸图，每一颗电芯清晰可见，电芯排列整齐密集，标注清晰的能量流向线。

画面右侧是两组电池的对比：左侧磷酸铁锂 LFP 电池组呈冷蓝色发光，体积紧凑，结构坚固，标注 12年 100万公里寿命、12C 充电倍率；右侧三元锂电池组已暗淡失效，被划上红色叉号，旁边是韩国电池巨头 Logo，整体黯淡无光。

左上方大数字 99% 表示中国市场磷酸铁锂占有率，以荧光绿显示。右下方显示 宁德时代 60% 市场份额，数字 60% 以荧光绿大字体呈现。画面底部显示 特斯拉 Semi 字样与 LFP 电池包的关联。"LFP 统治" 位于画面顶部居中位置，白色无衬线粗体字体，带有微弱发光效果。"""

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
    output_file = "slide_13.png"
    print("="*60)
    print("生成 slide_13 图片")
    print("="*60)
    result = generate_image(PROMPT, output_file)
    print(f"\n结果: {result}")
