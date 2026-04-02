#!/usr/bin/env python3
"""
批量生成幻灯片图片
从 prompts/v6/ 读取提示词，调用 ComfyUI API 生成图片
"""

import os
import sys
import json
import argparse
from pathlib import Path
from comfyui_api import ComfyUIAPI

def load_prompts(prompts_dir: str) -> dict:
    """加载所有提示词文件"""
    prompts = {}
    prompts_path = Path(prompts_dir)
    
    for prompt_file in sorted(prompts_path.glob("slide_*.txt")):
        slide_name = prompt_file.stem  # 例如：slide_00
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompts[slide_name] = f.read().strip()
    
    return prompts

def batch_generate(
    prompts_dir: str,
    output_dir: str,
    use_lightning: bool = True,
    comfyui_url: str = "http://100.111.221.7:8188"
):
    """
    批量生成图片
    
    Args:
        prompts_dir: 提示词目录（例如：prompts/v6）
        output_dir: 输出目录
        use_lightning: 是否使用 Lightning 模式
        comfyui_url: ComfyUI API 地址
    """
    # 加载提示词
    print("=" * 60)
    print("批量生成幻灯片图片")
    print("=" * 60)
    print(f"提示词目录：{prompts_dir}")
    print(f"输出目录：{output_dir}")
    print(f"模式：{'Lightning (4 步)' if use_lightning else '标准 (50 步)'}")
    print(f"ComfyUI: {comfyui_url}")
    print()
    
    prompts = load_prompts(prompts_dir)
    print(f"✅ 加载了 {len(prompts)} 个提示词")
    print()
    
    # 创建 ComfyUI API 客户端
    api = ComfyUIAPI(comfyui_url)
    
    # 批量生成
    success_count = 0
    failed_count = 0
    
    for slide_name, prompt_text in prompts.items():
        print(f"\n🔄 生成 {slide_name}...")
        
        try:
            # 生成图片
            result = api.generate_image(
                prompt_text=prompt_text,
                use_lightning=use_lightning,
                filename_prefix=f"{slide_name}"
            )
            
            if result.get("status") == "queued":
                success_count += 1
                print(f"  ✓ 任务已提交：{result['prompt_id']}")
            else:
                failed_count += 1
                print(f"  ✗ 提交失败：{result}")
                
        except Exception as e:
            failed_count += 1
            print(f"  ✗ 错误：{e}")
    
    # 总结
    print("\n" + "=" * 60)
    print(f"完成！成功：{success_count}, 失败：{failed_count}")
    print("=" * 60)
    
    return {
        "success": success_count,
        "failed": failed_count,
        "total": len(prompts)
    }

def main():
    parser = argparse.ArgumentParser(description="批量生成幻灯片图片")
    parser.add_argument(
        "--prompts-dir",
        default="tmp-slides/semi-ev3/prompts/v6",
        help="提示词目录（相对于 workspace）"
    )
    parser.add_argument(
        "--output-dir",
        default="tmp-slides/semi-ev3/slides",
        help="输出目录（相对于 workspace）"
    )
    parser.add_argument(
        "--lightning",
        action="store_true",
        default=True,
        help="使用 Lightning 模式（4 步快速生成）"
    )
    parser.add_argument(
        "--no-lightning",
        action="store_false",
        dest="lightning",
        help="不使用 Lightning 模式（50 步标准生成）"
    )
    parser.add_argument(
        "--comfyui-url",
        default="http://100.111.221.7:8188",
        help="ComfyUI API 地址"
    )
    
    args = parser.parse_args()
    
    # 获取 workspace 路径
    workspace_dir = Path(__file__).parent.parent.parent
    
    prompts_dir = workspace_dir / args.prompts_dir
    output_dir = workspace_dir / args.output_dir
    
    # 检查目录是否存在
    if not prompts_dir.exists():
        print(f"错误：提示词目录不存在：{prompts_dir}")
        sys.exit(1)
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 批量生成
    result = batch_generate(
        prompts_dir=str(prompts_dir),
        output_dir=str(output_dir),
        use_lightning=args.lightning,
        comfyui_url=args.comfyui_url
    )
    
    print(f"\n📊 统计:")
    print(f"  总计：{result['total']} 个 slides")
    print(f"  成功：{result['success']} 个")
    print(f"  失败：{result['failed']} 个")
    
    if result['failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
