#!/usr/bin/env python3
"""
生成 slide_00 v4 - 直接调用 ComfyUI API
"""
import json
import urllib.request
import time
import os

# 配置
COMFYUI_API = "http://100.111.221.7:8188"
WORKFLOW_FILE = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"
PROJECT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "slides")

# 读取提示词
with open(os.path.join(PROJECT_DIR, "prompts/slide_00_positive_v4.txt"), 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

with open(os.path.join(PROJECT_DIR, "prompts/slide_00_negative_v4.txt"), 'r', encoding='utf-8') as f:
    negative_prompt = f.read().strip()

print("="*60)
print("生成 slide_00 v4 图片")
print("="*60)
print(f"正向提示词长度：{len(positive_prompt)} 字符")
print(f"负向提示词长度：{len(negative_prompt)} 字符")
print()

# 加载工作流
with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修改节点参数
for node_id, node_data in workflow.items():
    if 'inputs' in node_data:
        if 'positive' in str(node_data.get('class_type', '')).lower() or node_id == '110':
            if 'prompt' in node_data['inputs']:
                node_data['inputs']['prompt'] = positive_prompt
                print(f"✓ 设置正向提示词 (节点 {node_id})")
        
        if 'negative' in str(node_data.get('class_type', '')).lower() or node_id == '111':
            if 'prompt' in node_data['inputs']:
                node_data['inputs']['prompt'] = negative_prompt
                print(f"✓ 设置负向提示词 (节点 {node_id})")
        
        if node_data.get('class_type') == 'EmptyLatentImage':
            node_data['inputs']['width'] = 1664
            node_data['inputs']['height'] = 928
            print(f"✓ 设置分辨率：1664x928")
        
        if node_data.get('class_type') == 'KSampler':
            node_data['inputs']['steps'] = 4
            node_data['inputs']['cfg'] = 1
            print(f"✓ 设置 Lightning 模式：Steps=4, CFG=1")

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        
        print()
        print("等待生成完成...")
        max_wait = 60
        waited = 0
        
        while waited < max_wait:
            time.sleep(2)
            waited += 2
            
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
            except:
                pass
        else:
            print(f"⚠ 超时，尝试获取结果...")
        
        if 'outputs' in result and prompt_id in result['outputs']:
            outputs = result['outputs'][prompt_id]
            for node_id, node_outputs in outputs.items():
                if 'images' in node_outputs:
                    for img_info in node_outputs['images']:
                        filename = img_info['filename']
                        subfolder = img_info.get('subfolder', '')
                        print(f"  输出文件：{filename}")
                        
                        print()
                        print("正在下载图片...")
                        image_url = f"{COMFYUI_API}/view?filename={filename}&subfolder={subfolder}"
                        
                        with urllib.request.urlopen(image_url) as img_resp:
                            image_data = img_resp.read()
                        
                        output_path = os.path.join(OUTPUT_DIR, 'slide_00_v4.png')
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
print("生成完成！")
print("="*60)
