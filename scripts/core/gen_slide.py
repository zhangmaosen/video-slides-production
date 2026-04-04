#!/usr/bin/env python3
"""
生成幻灯片图片
从 prompts/slide_XX/vN_positive.txt 和 vN_negative.txt 读取提示词，调用 ComfyUI API 生成图片

用法：
  python3 gen_slide.py --project projects/semi-ev3_20260403 --slide 00 --version 1
  python3 gen_slide.py --project projects/semi-ev3_20260403 --slide 00 --version 1 --lightning

输出：
  slides/slide_00_v1.png
"""

import os
import sys
import json
import argparse
import random
import time
import requests
from pathlib import Path

API_URL = "http://100.111.221.7:8188"

# WORKFLOW_PATH 放在 skill 目录下
SCRIPT_DIR = Path(__file__).parent  # scripts/core/
SKILL_DIR = SCRIPT_DIR.parent.parent  # video-slides-production/
WORKFLOW_PATH = SKILL_DIR / "ComfyUI" / "Qwen-Image-2512_ComfyUI.json"

def load_workflow():
    """加载 ComfyUI 工作流"""
    with open(WORKFLOW_PATH, 'r') as f:
        return json.load(f)

def generate_image(
    positive_prompt: str,
    negative_prompt: str,
    output_path: str,
    seed: int = None,
    width: int = 1280,
    height: int = 800,
    lightning: bool = False,
    api_url: str = API_URL
):
    """
    生成单张图片
    
    Args:
        positive_prompt: 正向提示词
        negative_prompt: 负向提示词
        output_path: 输出文件路径
        seed: 随机种子（None 则随机生成）
        width: 图片宽度
        height: 图片高度
        lightning: 是否使用 Lightning 模式
        api_url: ComfyUI API 地址
    """
    # 随机 seed（确保每次不同）
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    
    # 生成唯一的 prompt ID 防止 ComfyUI 重复
    import uuid
    prompt_id_suffix = str(uuid.uuid4())[:8]
    
    print(f"  Seed: {seed}")
    print(f"  Lightning: {lightning}")
    print(f"  Prompt ID suffix: {prompt_id_suffix}")
    
    # 加载工作流
    workflow = load_workflow()
    
    # 修改工作流
    for node_id, node in workflow.items():
        class_type = node.get('class_type')
        inputs = node.get('inputs', {})
        
        if class_type == 'CLIPTextEncode':
            # 设置提示词
            if 'text' in inputs:
                if 'negative' in node_id.lower() or 'neg' in node_id.lower():
                    inputs['text'] = negative_prompt
                else:
                    inputs['text'] = positive_prompt
        
        elif class_type == 'EmptySD3LatentImage':
            # 设置分辨率和 seed
            inputs['width'] = width
            inputs['height'] = height
            inputs['seed'] = seed
        
        elif class_type == 'PrimitiveBoolean':
            # Lightning 模式开关
            inputs['value'] = lightning
        
        elif class_type == 'KSampler':
            # 确保使用随机 seed
            inputs['seed'] = seed
    
    # 发送请求
    data = {"prompt": workflow}
    response = requests.post(f"{api_url}/prompt", json=data, timeout=30)
    result = response.json()
    task_id = result.get('prompt_id')
    
    if not task_id:
        print(f"  ✗ 提交失败：{result}")
        return False
    
    print(f"  Task ID: {task_id}")
    
    # 等待完成
    max_wait = 600
    start_time = time.time()
    while time.time() - start_time < max_wait:
        history = requests.get(f"{api_url}/history/{task_id}", timeout=10).json()
        if task_id in history:
            for node_id, node_output in history[task_id].get('outputs', {}).items():
                if 'images' in node_output:
                    for img in node_output['images']:
                        filename = img['filename']
                        img_response = requests.get(f"{api_url}/view?filename={filename}", timeout=30)
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"  ✓ 保存到: {output_path}")
            return True
        time.sleep(2)
    
    print(f"  ✗ 超时")
    return False

def main():
    parser = argparse.ArgumentParser(description="生成幻灯片图片")
    parser.add_argument("--project", required=True, help="项目目录（相对于 skills/video-slides-production）")
    parser.add_argument("--slide", required=True, help="幻灯片编号（如 00, 01）")
    parser.add_argument("--version", type=int, default=1, help="版本号（默认 1）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--width", type=int, default=1664, help="图片宽度（默认 1664）")
    parser.add_argument("--height", type=int, default=928, help="图片高度（默认 928）")
    parser.add_argument("--lightning", action="store_true", help="使用 Lightning 模式（4 steps, CFG 1）")
    parser.add_argument("--api-url", default=API_URL, help="ComfyUI API 地址")
    
    args = parser.parse_args()
    
    # 构建路径（相对于 skills/video-slides-production）
    project_dir = SKILL_DIR / args.project
    slide_num = args.slide
    version = args.version
    
    # 提示词文件路径
    prompt_dir = project_dir / "prompts" / f"slide_{slide_num}"
    positive_file = prompt_dir / f"v{version}_positive.txt"
    negative_file = prompt_dir / f"v{version}_negative.txt"
    
    # 输出文件路径
    output_file = project_dir / "slides" / f"slide_{slide_num}_v{version}.png"
    
    # 检查文件是否存在
    if not positive_file.exists():
        print(f"错误：正向提示词文件不存在: {positive_file}")
        sys.exit(1)
    if not negative_file.exists():
        print(f"错误：负向提示词文件不存在: {negative_file}")
        sys.exit(1)
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取提示词
    print(f"读取正向提示词: {positive_file}")
    with open(positive_file, 'r', encoding='utf-8') as f:
        positive_prompt = f.read().strip()
    
    print(f"读取负向提示词: {negative_file}")
    with open(negative_file, 'r', encoding='utf-8') as f:
        negative_prompt = f.read().strip()
    
    print(f"\n生成 slide_{slide_num}_v{version}...")
    
    # 生成图片
    success = generate_image(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        output_path=str(output_file),
        seed=args.seed,
        width=args.width,
        height=args.height,
        lightning=args.lightning,
        api_url=args.api_url
    )
    
    if success:
        print(f"\n✅ 完成！")
    else:
        print(f"\n❌ 失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
