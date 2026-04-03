#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

API_URL = "http://100.111.221.7:8188"

with open('ComfyUI/Qwen-Image-2512_ComfyUI.json', 'r') as f:
    workflow = json.load(f)

# slide_01 v9 prompt - 强化工程拆解风格 + 珍珠白涂装
positive_prompt = """混子说 + 硬核工程拆解爆炸图风格，线条粗细变化，诙谐严肃混合，技术细节清晰，结构透视感强，舞台感构图。

正面仰拍视角。

画面中央：一辆 Tesla Semi 电动重卡正面特写，**高光珍珠白涂装**（带有明显光泽感），哑光黑色覆盖式侧裙。巨大子弹头驾驶室向上延伸。封闭式前脸无进气格栅。极简 T 字形标志在车头正中央。流线型薄型电子后视镜。全景挡风玻璃。深蓝色 LED 灯带。

**工程爆炸图拆解**：电池组、驱动电机、线束等零件从车体中精确拆解，零件有明确的边界线和标注线（虚线），结构透视感强。

标注文字（大号字体，清晰可见）：
- 上方大号白色粗体字："开场爆点"
- 指向电池组件：大号红圈 + "电池"
- 指向驱动电机：大号红圈 + "电机"
- 指向产能标注：大号红圈 + "5万/年"

画面右侧：三辆传统燃油重卡剪影笨重，排气管喷出深灰色烟雾。

背景：货运港口，天际线晨曦。

舞台聚光灯效果。

工程拆解爆炸图风格，无营销烟雾特效。"""

negative_prompt = """AI generated, digital rendering, 3D render, photorealistic, smooth rendering, hyperrealistic

低画质，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节

银色车身，灰色涂装，传统卡车造型

电波组，电池组错误，电字错误，产能错误

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
                        with open('projects/semi-ev3_20260403/slides/slide_01_v9.png', 'wb') as f:
                            f.write(img_response.content)
                        print(f"Downloaded: {filename}")
            break
        time.sleep(2)
    else:
        print("Timeout")
else:
    print("Failed")
