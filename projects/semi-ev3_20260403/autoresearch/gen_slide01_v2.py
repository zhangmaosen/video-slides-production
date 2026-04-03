#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

API_URL = "http://100.111.221.7:8188"

with open('ComfyUI/Qwen-Image-2512_ComfyUI.json', 'r') as f:
    workflow = json.load(f)

# slide_01 v2 prompt - 强调 Tesla Semi 特征和文字标注
positive_prompt = """手绘漫画风格 + 工程爆炸图，正面特写视角。

画面中央：一辆 Tesla Semi 电动重卡正面特写傲然矗立，高光珍珠白涂装，哑光黑色侧裙。巨大子弹头驾驶室向上延伸与车顶流线融合。封闭式前脸无进气格栅。极简 T 字形标志在车头正中央。流线型电子后视镜。全景挡风玻璃。深蓝色贯穿式 LED 灯带划破黑暗车头。

电池组、驱动电机、线束如同精密爆炸图般从车体中悬浮拆解而出，标注清晰文字：
- "电"
- "电池组"
- "5 万台/年"

画面右侧：三辆传统燃油重卡侧身剪影笨重排列，轮毂老旧、结构臃肿，从排气管喷涌而出的废气化作深灰色烟雾，与 Tesla Semi 的零排放形成鲜明反差。

背景：灯火通明的全球货运港口，起重机整齐排列，天际线处晨曦光芒正破晓而出。

舞台聚光灯效果，线条粗细灵活变化。

上方白色粗体字："开场爆点"

手绘线条艺术风格，不是 3D 渲染。"""

negative_prompt = """3D渲染，数字渲染，Hyper-realistic，光滑渲染，金属反光过重，阴影细节过多

低画质，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节，过度光滑，AI生成感

银灰色车身，传统卡车造型，燃油重卡比例

Serni，Seri，Semo，Tesua，TESUA，Tsela，TSELA 拼写错误

文字错别字，文字乱码，模糊文字，标注缺失"""

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
                        with open('projects/semi-ev3_20260403/slides/slide_01_v2.png', 'wb') as f:
                            f.write(img_response.content)
                        print(f"Downloaded: {filename}")
            break
        time.sleep(2)
    else:
        print("Timeout")
else:
    print("Failed")
