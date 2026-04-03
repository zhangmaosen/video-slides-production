#!/usr/bin/env python3
"""
生成 slide_00 v4 - 标准模式 1280x800, steps=50
"""
import json
import urllib.request
import time
import os

COMFYUI_API = "http://100.111.221.7:8188"
WORKFLOW_FILE = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"
PROJECT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "slides")

# 读取提示词
with open(os.path.join(PROJECT_DIR, "prompts/slide_00_positive_v4.txt"), 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

negative_prompt = """低画质，低分辨率，肢体畸形，手指畸形，过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲文字
文字错误，错别字，文字乱码，模糊文字，奇怪符号，异体字
Sermi，Seemi，Semi 变形，Tesla 变体拼写
标题错误，标题有多余"说"字，"特斯拉说 Semi"错误写法
"拆翻"错误写法，必须是"掀翻"
缺少副标题"一场输不起的商业货运革命"
高顶厢式货车，高顶设计，方正造型，厢式货车造型
面包车，小型电动车，轿车，越野车，城市用车
普通卡车造型，非半挂牵引车
银色车身，灰色涂装，金属银，metallic silver，silver gray
夸张的爆炸特效，过度夸张的背景，混乱的背景
Prompt 说明文字，提示词说明，任何形式的说明性文字
三叉戟 logo，星形 logo，非 T 型 logo
轮胎棱角生硬，轮胎过度锐利，轮毂金属感刺眼"""

print("="*60)
print("生成 slide_00 v4 图片 - 标准模式")
print("="*60)
print(f"正向提示词长度：{len(positive_prompt)} 字符")
print(f"负向提示词长度：{len(negative_prompt)} 字符")
print()

# 加载工作流
with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修改节点参数 - 标准模式 1280x800, steps=50
for node_id, node_data in workflow.items():
    if 'inputs' in node_data:
        # 正向提示词
        if node_data.get('class_type') == 'CLIPTextEncode' and 'positive' in str(node_data.get('_meta', {}).get('title', '')).lower():
            node_data['inputs']['text'] = positive_prompt
            print(f"✓ 设置正向提示词 (节点 {node_id})")
        
        # 负向提示词
        if node_data.get('class_type') == 'CLIPTextEncode' and 'negative' in str(node_data.get('_meta', {}).get('title', '')).lower():
            node_data['inputs']['text'] = negative_prompt
            print(f"✓ 设置负向提示词 (节点 {node_id})")
        
        # 分辨率 1280x800
        if node_data.get('class_type') == 'EmptySD3LatentImage':
            node_data['inputs']['width'] = 1280
            node_data['inputs']['height'] = 800
            print(f"✓ 设置分辨率：1280x800")
        
        # Steps = 50 (标准模式，不开 Lightning)
        if node_data.get('class_type') == 'PrimitiveInt' and node_data.get('_meta', {}).get('title') == 'Steps':
            if 'value' in node_data['inputs']:
                node_data['inputs']['value'] = 50
                print(f"✓ 设置 Steps=50 (节点 {node_id})")
        
        # CFG = 4
        if node_data.get('class_type') == 'PrimitiveFloat' and node_data.get('_meta', {}).get('title') == 'CFG':
            if 'value' in node_data['inputs']:
                node_data['inputs']['value'] = 4
                print(f"✓ 设置 CFG=4 (节点 {node_id})")
        
        # 确保 Lightning 关闭
        if node_data.get('class_type') == 'PrimitiveBoolean' and node_data.get('_meta', {}).get('title') == 'Enable 4 Steps LoRA?':
            node_data['inputs']['value'] = False
            print(f"✓ 关闭 Lightning LoRA (节点 {node_id})")

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
        max_wait = 300
        waited = 0
        
        while waited < max_wait:
            time.sleep(5)
            waited += 5
            
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
            except Exception as e:
                print(f"  检查中... ({waited}s) - {e}")
        else:
            print(f"⚠ 超时，尝试获取结果...")
        
        # 获取输出
        if prompt_id:
            try:
                history_url = f"{COMFYUI_API}/history/{prompt_id}"
                with urllib.request.urlopen(history_url, timeout=10) as hist_resp:
                    history = json.loads(hist_resp.read().decode('utf-8'))
                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})
                        for node_id_out, node_outputs in outputs.items():
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
            except Exception as e:
                print(f"✗ 获取结果失败：{e}")
                
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
