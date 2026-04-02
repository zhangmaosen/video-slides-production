#!/usr/bin/env python3
"""
从 ComfyUI 服务器下载生成的图片
"""

import os
import sys
import json
from urllib import request
from pathlib import Path

def download_image(comfyui_url: str, filename: str, output_dir: str) -> bool:
    """下载单张图片"""
    try:
        # ComfyUI 图片 URL 格式
        image_url = f"{comfyui_url}/view?filename={filename}&type=output"
        
        # 创建输出目录
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 下载图片
        req = request.Request(image_url)
        response = request.urlopen(req)
        
        with open(output_path, 'wb') as f:
            f.write(response.read())
        
        print(f"✅ 已下载：{filename}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败 {filename}: {e}")
        return False

def get_slide_filenames(comfyui_url: str, slide_count: int = 17) -> list:
    """从 ComfyUI 历史获取所有 slide 的文件名"""
    try:
        response = request.urlopen(f"{comfyui_url}/history?max_items=100")
        history = json.loads(response.read().decode('utf-8'))
        
        filenames = {}
        
        for pid, task in history.items():
            if 'prompt' in task:
                prompt = task['prompt']
                if isinstance(prompt, list) and len(prompt) > 2:
                    prompt_dict = prompt[2]
                    if '60' in prompt_dict:
                        prefix = prompt_dict['60']['inputs'].get('filename_prefix', '')
                        if prefix.startswith('slide_'):
                            # 获取实际文件名
                            outputs = task.get('outputs', {})
                            for node_id, node_out in outputs.items():
                                if 'images' in node_out:
                                    for img in node_out['images']:
                                        filename = img.get('filename')
                                        if filename:
                                            filenames[prefix] = filename
                                            break
        
        return list(filenames.values())
        
    except Exception as e:
        print(f"❌ 获取文件名失败：{e}")
        return []

def download_all_images(comfyui_url: str, output_dir: str, slide_count: int = 17):
    """下载所有 slide 图片"""
    print("=" * 60)
    print(f"下载 {slide_count} 个 slide 图片")
    print("=" * 60)
    print(f"ComfyUI: {comfyui_url}")
    print(f"输出目录：{output_dir}")
    print()
    
    # 获取实际文件名
    print("正在获取文件名...")
    filenames = get_slide_filenames(comfyui_url, slide_count)
    print(f"找到 {len(filenames)} 个文件")
    print()
    
    success_count = 0
    failed_count = 0
    
    # 下载所有找到的文件
    for filename in filenames:
        if download_image(comfyui_url, filename, output_dir):
            success_count += 1
        else:
            failed_count += 1
    
    # 总结
    print()
    print("=" * 60)
    print(f"完成！成功：{success_count}, 失败：{failed_count}")
    print("=" * 60)
    
    return {
        "success": success_count,
        "failed": failed_count,
        "total": len(filenames)
    }

def main():
    # 配置
    comfyui_url = "http://100.111.221.7:8188"
    output_dir = "/Users/maosen/.openclaw/workspace-rex/tmp-slides/semi-ev3/slides"
    
    # 下载所有图片
    result = download_all_images(comfyui_url, output_dir, slide_count=17)
    
    print(f"\n📊 统计:")
    print(f"  总计：{result['total']} 个 slides")
    print(f"  成功：{result['success']} 个")
    print(f"  失败：{result['failed']} 个")
    
    if result['failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
