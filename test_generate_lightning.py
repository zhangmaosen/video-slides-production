#!/usr/bin/env python3
"""
测试生成单张图片 - Lightning LoRA 模式
"""
import json
import urllib.request
import os
import time

# 加载配置
with open('comfyui_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

COMFYUI_API = config['comfyui_api']
NEGATIVE_PROMPT = config['negative_prompt']
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), config['output_dir'])

# 读取 slide_00 的提示词（使用 v6 版本）
PROMPT_PATH = '../../tmp-slides/semi-ev3/prompts/v6/slide_00.txt'
if not os.path.exists(PROMPT_PATH):
    PROMPT_PATH = '../../tmp-slides/semi-ev3/prompts/v5/slide_00.txt'

with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

print("="*60)
print("测试生成 Slide 00 (Lightning LoRA 模式)")
print("="*60)
print(f"ComfyUI API: {COMFYUI_API}")
print(f"提示词长度：{len(positive_prompt)} 字符")
print(f"模式：Lightning (Steps=4, CFG=1)")
print()

# 加载工作流
with open('Qwen-Image-2512_Workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修改节点参数 - Lightning 模式
if '110' in workflow:  # Positive prompt
    workflow['110']['inputs']['prompt'] = positive_prompt
    print(f"✓ 设置正向提示词 ({len(positive_prompt)} 字符)")

if '111' in workflow:  # Negative prompt
    workflow['111']['inputs']['prompt'] = NEGATIVE_PROMPT
    print(f"✓ 设置负向提示词 ({len(NEGATIVE_PROMPT)} 字符)")

if '3' in workflow:  # KSampler - Lightning 模式
    workflow['3']['inputs']['steps'] = 4  # Lightning: 4 steps
    workflow['3']['inputs']['cfg'] = 1    # Lightning: CFG=1
    print(f"✓ 设置 Lightning 模式：Steps=4, CFG=1")

if '87' in workflow:  # Empty Latent
    workflow['87']['inputs']['width'] = config['default_settings']['width']
    workflow['87']['inputs']['height'] = config['default_settings']['height']
    print(f"✓ 设置分辨率：{config['default_settings']['width']}x{config['default_settings']['height']}")

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 发送到 ComfyUI
print()
print("正在发送到 ComfyUI...")
start_time = time.time()

data = json.dumps({"prompt": workflow}).encode('utf-8')
req = urllib.request.Request(
    f"{COMFYUI_API}/prompt",
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read().decode('utf-8'))
        submit_time = time.time() - start_time
        print(f"✓ 请求成功！({submit_time:.2f}s)")
        print(f"  Prompt ID: {result.get('prompt_id', 'N/A')}")
        
        prompt_id = result.get('prompt_id')
        
        # 等待生成完成
        print()
        print("等待生成完成...")
        max_wait = 60  # 最多等待 60 秒
        waited = 0
        
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
            # 检查生成状态
            try:
                history_url = f"{COMFYUI_API}/history/{prompt_id}"
                with urllib.request.urlopen(history_url, timeout=5) as hist_resp:
                    history = json.loads(hist_resp.read().decode('utf-8'))
                    if prompt_id in history:
                        status = history[prompt_id].get('status', {})
                        status_str = status.get('status_str', 'unknown')
                        
                        if status_str == 'success':
                            print(f"✓ 生成完成！({waited}s)")
                            break
                        elif status_str == 'running':
                            print(f"  生成中... ({waited}s)")
                        else:
                            print(f"  状态：{status_str} ({waited}s)")
            except:
                pass
        else:
            print(f"⚠ 超时，尝试获取结果...")
        
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
                        output_path = os.path.join(OUTPUT_DIR, 'slide_00_lightning.png')
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        total_time = time.time() - start_time
                        print(f"✓ 图片已保存到：{output_path}")
                        print(f"  文件大小：{len(image_data):,.0f} 字节")
                        print(f"  总耗时：{total_time:.2f} 秒")
                        
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
