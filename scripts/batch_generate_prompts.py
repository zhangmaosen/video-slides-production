#!/usr/bin/env python3
"""
批量生成图片提示词 - 通用脚本
使用元提示词模板 + 项目内容
"""
import subprocess
import json
import os
import sys
import argparse

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)  # video-slides-production 目录

def load_meta_template(template_path):
    """加载元提示词模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def build_prompt(meta_template, style, title, viewpoint, script, background):
    """构建完整的提示词"""
    
    # 构建用户输入部分
    user_input = f"""
- 视觉风格：{style}
- 标题：{title}
- 观点：{viewpoint}
- 逐字稿：{script}
- 背景知识：{background}
"""
    
    # 如果模板中有用户输入占位符，替换它
    if "{用户输入}" in meta_template:
        meta_template = meta_template.replace("{用户输入}", user_input)
    else:
        # 否则追加到末尾
        meta_template += f"\n---\n\n# 用户输入\n{user_input}"
    
    return meta_template

def generate_prompt(api_key, url, model, prompt):
    """调用 API 生成提示词"""
    response = subprocess.run([
        'curl', '-X', 'POST', url,
        '-H', f'Authorization: Bearer {api_key}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }, ensure_ascii=False)
    ], capture_output=True, text=True, timeout=60)
    
    if response.returncode != 0:
        raise Exception(f"API 调用失败：{response.stderr}")
    
    result = json.loads(response.stdout)
    
    if 'content' in result and isinstance(result['content'], list):
        content = ""
        for item in result['content']:
            if item.get('type') == 'text':
                content += item.get('text', '')
        return content
    elif 'choices' in result:
        return result['choices'][0]['message']['content']
    else:
        raise Exception("无法解析 API 响应")

def main():
    parser = argparse.ArgumentParser(description='批量生成图片提示词')
    parser.add_argument('--project', required=True, help='项目名称（workspace 下的目录名）')
    parser.add_argument('--content-file', required=True, help='slides 内容文件路径（相对于项目目录）')
    parser.add_argument('--output-dir', required=True, help='输出目录（相对于项目目录）')
    parser.add_argument('--style', default='混子说风格融合硬核工程拆解素描风格', help='视觉风格')
    parser.add_argument('--api-key', help='API Key（可选，默认从环境变量读取）')
    parser.add_argument('--api-url', default='https://api.minimaxi.com/anthropic/v1/messages', help='API URL')
    parser.add_argument('--model', default='MiniMax-M2.7', help='AI 模型')
    
    args = parser.parse_args()
    
    # 路径配置
    project_dir = os.path.join(WORKSPACE_DIR, args.project)
    content_file = os.path.join(project_dir, args.content_file)
    output_dir = os.path.join(project_dir, args.output_dir)
    
    # 元模板路径
    meta_template_path = os.path.join(WORKSPACE_DIR, 'META_PROMPT.md')
    
    # API 配置
    api_key = args.api_key or os.environ.get('MINIMAX_API_KEY')
    if not api_key:
        print("错误：请提供 API Key（使用 --api-key 或设置 MINIMAX_API_KEY 环境变量）")
        sys.exit(1)
    
    # 加载配置
    print("="*60)
    print("批量生成图片提示词")
    print("="*60)
    print(f"项目目录：{project_dir}")
    print(f"元模板：{meta_template_path}")
    print(f"输出目录：{output_dir}")
    print()
    
    # 加载元模板
    print("正在加载元提示词模板...")
    meta_template = load_meta_template(meta_template_path)
    print(f"  ✓ 元模板已加载 ({len(meta_template)} 字符)")
    
    # 加载 slides 内容
    print("正在加载 slides 内容...")
    with open(content_file, 'r', encoding='utf-8') as f:
        slides_content = json.load(f)
    print(f"  ✓ Slides 内容已加载 ({len(slides_content)} 个 slides)")
    print()
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量生成
    success_count = 0
    fail_count = 0
    
    for slide_key, slide_data in slides_content.items():
        output_path = os.path.join(output_dir, f"{slide_key}.txt")
        
        # 跳过已生成的
        if os.path.exists(output_path):
            print(f"⏭️  {slide_key} - 已存在，跳过")
            success_count += 1
            continue
        
        print(f"🔄  生成 {slide_key}...")
        
        try:
            # 构建提示词
            prompt = build_prompt(
                meta_template,
                args.style,
                slide_data.get('title', ''),
                slide_data.get('viewpoint', ''),
                slide_data.get('script', ''),
                slide_data.get('background', '')
            )
            
            # 调用 API
            content = generate_prompt(api_key, args.api_url, args.model, prompt)
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ 已保存 ({len(content)} 字符)")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ 错误：{str(e)[:100]}")
            fail_count += 1
        
        print()
    
    print("="*60)
    print(f"完成！成功：{success_count}, 失败：{fail_count}")
    print("="*60)

if __name__ == '__main__':
    main()
