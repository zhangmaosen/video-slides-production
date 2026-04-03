#!/usr/bin/env python3
"""
测试生成单张图片 - 使用正确的工作流格式
"""
import json
import urllib.request
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
print("测试生成 Slide 00 (最终版)")
print("="*60)
print(f"ComfyUI API: {COMFYUI_API}")
print(f"提示词长度：{len(positive_prompt)} 字符")
print()

# 加载工作流
with open('Qwen-Image-2512_Workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修改节点参数
if '110' in workflow:  # Positive prompt
    workflow['110']['inputs']['prompt'] = positive_prompt
    print(f"✓ 设置正向提示词 ({len(positive_prompt)} 字符)")

if '111' in workflow:  # Negative prompt
    workflow['111']['inputs']['prompt'] = NEGATIVE_PROMPT
    print(f"✓ 设置负向提示词 ({len(NEGATIVE_PROMPT)} 字符)")

if '3' in workflow:  # KSampler
    workflow['3']['inputs']['steps'] = config['default_settings']['steps']
    workflow['3']['inputs']['cfg'] = config['default_settings']['cfg']
    print(f"✓ 设置 Steps: {config['default_settings']['steps']}, CFG: {config['default_settings']['cfg']}")

if '87' in workflow:  # Empty Latent
    workflow['87']['inputs']['width'] = config['default_settings']['width']
    workflow['87']['inputs']['height'] = config['default_settings']['height']
    print(f"✓ 设置分辨率：{config['default_settings']['width']}x{config['default_settings']['height']}")

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
    with urllib.request.urlopen(req, timeout=120) as response:
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
    error_body = e.read().decode('utf-8')
    print(f"  错误详情：{error_body[:300]}")
except urllib.error.URLError as e:
    print(f"✗ URL 错误：{e.reason}")
except Exception as e:
    print(f"✗ 错误：{e}")

print()
print("="*60)
print("测试完成！")
print("="*60)
