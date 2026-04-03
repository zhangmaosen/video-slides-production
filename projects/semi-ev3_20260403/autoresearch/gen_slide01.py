#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time

API_URL = "http://100.111.221.7:8188"

with open('ComfyUI/Qwen-Image-2512_ComfyUI.json', 'r') as f:
    workflow = json.load(f)

# slide_01 prompt
positive_prompt = """工程爆炸图风格 + 手绘线条艺术，一幅极具舞台感的商业对决画面在眼前展开：画面中央偏左，一辆 Tesla Semi 电动重卡正面特写傲然矗立，银灰色金属车身泛着冷峻光泽，线条锋利如切削般锐利，深蓝色贯穿式 LED 灯带划破黑暗车头，超大尺寸挡风玻璃映射出前方货运码头的繁忙灯火，电池组、驱动电机、线束如同精密爆炸图般从车体中悬浮拆解而出，标注着"电""电池组""5 万台/年"等技术细节；画面右侧，三辆传统燃油重卡侧身剪影笨重排列，轮毂老旧、结构臃肿，从排气管喷涌而出的废气化作深灰色烟雾，与 Tesla Semi 的零排放形成鲜明反差；背景是灯火通明的全球货运港口，起重机整齐排列，货轮集装箱层层叠叠，天际线处晨曦光芒正破晓而出；整体光影采用舞台聚光灯效果，冷色主光从左上方投射，暖色补光从右下方呼应，形成强烈戏剧张力，线条粗细随距离和重要性灵活变化，近景粗犷有力、远景细腻渐隐；画面上方三分之一处，白色粗体发光字体静静悬浮——"开场爆点"

手绘线条艺术风格，不是 3D 渲染。"""

negative_prompt = """3D渲染，数字渲染，Hyper-realistic，光滑渲染，金属反光过重，阴影细节过多

低画质，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节，过度光滑

Serni，Seri，Semo，Tesua，TESUA，Tsela，TSELA，SEM'I 拼写错误

文字错别字，文字乱码，模糊文字"""

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
                        with open('projects/semi-ev3_20260403/slides/slide_01_v1.png', 'wb') as f:
                            f.write(img_response.content)
                        print(f"Downloaded: {filename}")
            break
        time.sleep(2)
    else:
        print("Timeout")
else:
    print("Failed")
