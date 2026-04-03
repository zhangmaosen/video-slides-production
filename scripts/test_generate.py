#!/usr/bin/env python3
"""
测试生成单张图片 - 验证 ComfyUI 配置
"""
import json
import urllib.request
import urllib.parse
import base64
import os

# 加载配置
with open('comfyui_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

COMFYUI_API = config['comfyui_api']
NEGATIVE_PROMPT = config['negative_prompt']
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), config['output_dir'])

# 读取 slide_00 的提示词
with open('../../tmp-slides/semi-ev3/prompts/v5/slide_00.txt', 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

print("="*60)
print("测试生成 Slide 00")
print("="*60)
print(f"ComfyUI API: {COMFYUI_API}")
print(f"提示词长度：{len(positive_prompt)} 字符")
print(f"输出目录：{OUTPUT_DIR}")
print()

# 加载工作流
with open('Qwen-Image-2512_ComfyUI.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修改工作流中的参数
# 1. 修改提示词节点 (node 227)
for node in workflow['nodes']:
    if node.get('id') == 227:  # Positive prompt
        if 'widgets_values' in node:
            node['widgets_values'][0] = positive_prompt
            print(f"✓ 设置正向提示词 ({len(positive_prompt)} 字符)")
    elif node.get('id') == 228:  # Negative prompt
        if 'widgets_values' in node:
            node['widgets_values'][0] = NEGATIVE_PROMPT
            print(f"✓ 设置负向提示词 ({len(NEGATIVE_PROMPT)} 字符)")
    elif node.get('id') == 232:  # Image size
        if 'widgets_values' in node:
            node['widgets_values'][0] = config['default_settings']['width']
            node['widgets_values'][1] = config['default_settings']['height']
            print(f"✓ 设置分辨率：{config['default_settings']['width']}x{config['default_settings']['height']}")

# 2. 修改 subgraph 中的节点（如果存在）
if 'definitions' in workflow and 'subgraphs' in workflow['definitions']:
    for subgraph in workflow['definitions']['subgraphs']:
        if 'nodes' in subgraph:
            for node in subgraph['nodes']:
                if node.get('id') == 227:
                    if 'widgets_values' in node:
                        node['widgets_values'][0] = positive_prompt
                elif node.get('id') == 228:
                    if 'widgets_values' in node:
                        node['widgets_values'][0] = NEGATIVE_PROMPT
                elif node.get('id') == 232:
                    if 'widgets_values' in node:
                        node['widgets_values'][0] = config['default_settings']['width']
                        node['widgets_values'][1] = config['default_settings']['height']

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 发送到 ComfyUI
print()
print("正在发送到 ComfyUI...")

data = json.dumps({"prompt": workflow}).encode('utf-8')
req = urllib.request.Request(
    f"{COMFYUI_API}/prompt",
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✓ 请求成功！")
        print(f"  Prompt ID: {result.get('prompt_id', 'N/A')}")
        
        # 获取输出路径
        if 'outputs' in result and 'prompt_id' in result['outputs']:
            outputs = result['outputs']['prompt_id']
            for node_id, node_outputs in outputs.items():
                if 'images' in node_outputs:
                    for img_info in node_outputs['images']:
                        filename = img_info['filename']
                        subfolder = img_info.get('subfolder', '')
                        print(f"  输出文件：{filename}")
                        
                        # 下载图片
                        print()
                        print("正在下载图片...")
                        image_url = f"{COMFYUI_API}/view?filename={filename}&subfolder={subfolder}"
                        
                        with urllib.request.urlopen(image_url) as img_resp:
                            image_data = img_resp.read()
                        
                        # 保存到项目目录
                        output_path = os.path.join(OUTPUT_DIR, 'slide_00_test.png')
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"✓ 图片已保存到：{output_path}")
                        print(f"  文件大小：{len(image_data)} 字节")
                        
except urllib.error.HTTPError as e:
    print(f"✗ HTTP 错误：{e.code} {e.reason}")
    print(f"  响应：{e.read().decode('utf-8')}")
except urllib.error.URLError as e:
    print(f"✗ URL 错误：{e.reason}")
except Exception as e:
    print(f"✗ 错误：{e}")

print()
print("="*60)
print("测试完成！")
print("="*60)
