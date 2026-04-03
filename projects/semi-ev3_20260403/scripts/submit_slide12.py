#!/usr/bin/env python3
"""Submit slide_12 job only - no polling"""
import json
import urllib.request
import urllib.error
import os
import sys
import time
import random

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"

NEGATIVE_PROMPT = """低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲，文字错别字，文字乱码，模糊文字，奇怪符号，AI 字体，英文文字，错误数字，混乱排版"""

PROMPT = """混子说手绘 + 硬核工程拆解爆炸图风格，线条粗细变化，诙谐严肃混合，技术细节清晰，结构透视感强，舞台感构图。画面采用舞台感构图，中央是一辆特斯拉 Semi 电动半挂重型卡车正在进行兆瓦快充，车身采用哑光黑色涂装，全封闭车头设计，细长贯穿式 LED 前灯带发出冷冽蓝光，科技蓝色光纹在车身表面流动。驾驶舱玻璃透明，内部冷蓝发光。巨大的充电枪线缆从车身左侧伸出，连接至兆瓦充电桩，充电接口发出强烈的蓝白色能量光芒，光芒四射。

画面右侧是充电桩局部特写，屏幕显示 30 分钟回血 60% 的数据，以荧光绿色大字体呈现。画面左侧分为上下两个区域：上方是中国换电场景，一辆 Semi 正在换电站进行电池包整体更换，电池包从底盘弹出呈爆炸图展开，结构细节清晰，标注"换电为主"；下方是出海快充场景，显示 Windrose 兼容兆瓦快充标准，35 分钟 10% 充至 80%，标注"快充为辅"。

背景是简洁的深色渐变舞台，营造时间凝固的戏剧性时刻。"补能战略" 位于画面顶部居中位置，白色无衬线粗体字体，带有微弱发光效果。"30分钟 60%" 位于画面右上角，荧光绿数字配合深色半透明背景框。"35分钟 10%→80%" 位于左下角换电区域下方，中文字体标注。"""

def submit_job():
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    seed = random.randint(0, 2**32 - 1)
    workflow["238:227"]["inputs"]["text"] = PROMPT
    workflow["238:228"]["inputs"]["text"] = NEGATIVE_PROMPT
    workflow["238:232"]["inputs"]["width"] = 1664
    workflow["238:232"]["inputs"]["height"] = 928
    workflow["238:230"]["inputs"]["seed"] = seed
    workflow["238:224"]["inputs"]["value"] = 50
    workflow["238:223"]["inputs"]["value"] = 4

    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(f"{API_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})

    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        prompt_id = result.get('prompt_id')
        print(f"SUBMITTED|{prompt_id}|{seed}", flush=True)
        return prompt_id, seed

if __name__ == "__main__":
    submit_job()
