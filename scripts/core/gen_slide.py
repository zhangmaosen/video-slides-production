#!/usr/bin/env python3
"""
生成幻灯片图片
从 prompts/slide_xx_positive.txt 和 slide_xx_negative.txt 读取提示词，调用 ComfyUI API 生成图片

正向和负向提示词分开文件存储：
- slide_xx_positive.txt：正向提示词（画面描述）
- slide_xx_negative.txt：负向提示词（需要避免的问题）
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
WORKFLOW_PATH = Path(__file__).parent.parent.parent / "ComfyUI" / "Qwen-Image-2512_ComfyUI.json"

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
        api_url: ComfyUI API 地址
    """
    # 随机 seed
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    
    print(f"  Seed: {seed}")
    
    # 加载工作流
    workflow = load_workflow()
    
    # 修改工作流
    for node_id, node in workflow.items():
        if node.get('class_type') == 'CLIPTextEncode':
            inputs = node.get('inputs', {})
            if 'text' in inputs:
                # 判断是正向还是负向
                if 'negative' in node_id.lower() or 'neg' in node_id.lower():
                    inputs['text'] = negative_prompt
                else:
                    inputs['text'] = positive_prompt
        elif node.get('class_type') == 'EmptySD3LatentImage':
            node['inputs']['width'] = width
            node['inputs']['height'] = height
            node['inputs']['seed'] = seed
        elif node.get('class_type') == 'PrimitiveBoolean':
            node['inputs']['value'] = False
    
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
    max_wait = 300
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
    parser = argparse.ArgumentParser(description="生成幻灯片图片（正向负向分开）")
    parser.add_argument("--project", required=True, help="项目目录")
    parser.add_argument("--slide", required=True, help="幻灯片编号（如 00, 01）")
    parser.add_argument("--positive", help="正向提示词文件路径")
    parser.add_argument("--negative", help="负向提示词文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--api-url", default=API_URL, help="ComfyUI API 地址")
    
    args = parser.parse_args()
    
    # 构建路径
    project_dir = Path(args.project)
    slide_num = args.slide
    
    # 默认文件路径
    prompts_dir = project_dir / "prompts"
    positive_file = args.positive or prompts_dir / f"slide_{slide_num}_positive.txt"
    negative_file = args.negative or prompts_dir / f"slide_{slide_num}_negative.txt"
    output_file = args.output or project_dir / "slides" / f"slide_{slide_num}.png"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取提示词
    print(f"读取正向提示词: {positive_file}")
    with open(positive_file, 'r', encoding='utf-8') as f:
        positive_prompt = f.read().strip()
    
    print(f"读取负向提示词: {negative_file}")
    with open(negative_file, 'r', encoding='utf-8') as f:
        negative_prompt = f.read().strip()
    
    print(f"\n生成 slide_{slide_num}...")
    
    # 生成图片
    success = generate_image(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        output_path=str(output_file),
        seed=args.seed,
        api_url=args.api_url
    )
    
    if success:
        print(f"\n✅ 完成！")
    else:
        print(f"\n❌ 失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
