#!/usr/bin/env python3
"""
监控 ComfyUI 任务进度并下载完成的图片
"""

import time
import json
from urllib import request
from pathlib import Path

def get_queue_status(comfyui_url: str) -> dict:
    """获取队列状态"""
    try:
        response = request.urlopen(f"{comfyui_url}/queue")
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ 获取队列失败：{e}")
        return {"queue_running": [], "queue_pending": []}

def get_history(comfyui_url: str) -> dict:
    """获取历史记录"""
    try:
        response = request.urlopen(f"{comfyui_url}/history?max_items=100")
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ 获取历史失败：{e}")
        return {}

def get_slide_tasks(comfyui_url: str) -> list:
    """获取所有 slide 任务"""
    history = get_history(comfyui_url)
    tasks = []
    
    for pid, task in history.items():
        if 'prompt' in task:
            prompt = task['prompt']
            if isinstance(prompt, list) and len(prompt) > 2:
                prompt_dict = prompt[2]
                if '60' in prompt_dict:
                    prefix = prompt_dict['60']['inputs'].get('filename_prefix', '')
                    if prefix.startswith('slide_'):
                        outputs = task.get('outputs', {})
                        has_images = any('images' in out for out in outputs.values())
                        tasks.append({
                            'prefix': prefix,
                            'prompt_id': pid,
                            'completed': has_images
                        })
    
    return tasks

def download_image(comfyui_url: str, filename: str, output_dir: str) -> bool:
    """下载单张图片"""
    try:
        image_url = f"{comfyui_url}/view?filename={filename}&type=output"
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        req = request.Request(image_url)
        response = request.urlopen(req)
        
        with open(output_path, 'wb') as f:
            f.write(response.read())
        
        print(f"✅ 已下载：{filename}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 {filename}: {e}")
        return False

def main():
    comfyui_url = "http://100.111.221.7:8188"
    output_dir = "/Users/maosen/.openclaw/workspace-rex/tmp-slides/semi-ev3/slides"
    
    print("=" * 60)
    print("ComfyUI 任务监控和下载")
    print("=" * 60)
    print(f"ComfyUI: {comfyui_url}")
    print(f"输出目录：{output_dir}")
    print()
    
    # 获取当前队列状态
    queue = get_queue_status(comfyui_url)
    print(f"📊 队列状态:")
    print(f"  运行中：{len(queue.get('queue_running', []))} 个任务")
    print(f"  等待中：{len(queue.get('queue_pending', []))} 个任务")
    print()
    
    # 获取所有 slide 任务
    tasks = get_slide_tasks(comfyui_url)
    print(f"📋 找到 {len(tasks)} 个 slide 任务")
    
    completed_count = sum(1 for t in tasks if t['completed'])
    pending_count = len(tasks) - completed_count
    
    print(f"  已完成：{completed_count} 个")
    print(f"  处理中：{pending_count} 个")
    print()
    
    # 下载已完成的图片
    if completed_count > 0:
        print(f"📥 下载 {completed_count} 个已完成的图片...")
        print()
        
        for task in tasks:
            if task['completed']:
                # 获取实际文件名
                history = get_history(comfyui_url)
                task_data = history.get(task['prompt_id'], {})
                outputs = task_data.get('outputs', {})
                
                for node_id, node_out in outputs.items():
                    if 'images' in node_out:
                        for img in node_out['images']:
                            filename = img.get('filename')
                            if filename:
                                download_image(comfyui_url, filename, output_dir)
                                break
    
    print()
    print("=" * 60)
    
    # 返回状态
    return {
        "running": len(queue.get('queue_running', [])),
        "pending": len(queue.get('queue_pending', [])),
        "completed": completed_count,
        "total": len(tasks)
    }

if __name__ == "__main__":
    result = main()
    print(f"\n最终状态:")
    print(f"  运行中：{result['running']}")
    print(f"  等待中：{result['pending']}")
    print(f"  已完成：{result['completed']}/{result['total']}")
