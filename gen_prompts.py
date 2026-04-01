#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频幻灯片提示词生成器
自动读取slides_content.md，执行元模板，调用LLM生成500+字提示词
"""

import os
import sys
import json
import subprocess
import time

# ============== 配置 ==============
# LLM API配置 - minimax-portal (anthropic API)
LLM_API_URL = "https://api.minimaxi.com/anthropic/v1/messages"
LLM_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
LLM_MODEL = "MiniMax-M2.7"

# 风格配置
STYLE = "手绘漫画风格，线条粗细变化，水墨灰阶，诙谐严肃混合，混子说风格，舞台感构图"

# 元提示词模板
PROMPT_TEMPLATE = """你是一位被关在逻辑牢笼里的幻视艺术家，你擅长的风格是{输入风格}。你满脑子都是诗和远方，但双手却不受控制地只想将用户的提示词，转化为一段忠实于原始意图、细节饱满、富有美感、可直接被文生图模型使用的终极视觉描述。任何一点模糊和比喻都会让你浑身难受。你的工作流程严格遵循一个逻辑序列：首先，你会分析并锁定用户提示词中不可变更的核心要素：主体、数量、动作、状态，以及任何指定的IP名称、颜色、文字等。这些是你必须绝对保留的基石。接着，你会判断提示词是否需要**"生成式推理"**。当用户的需求并非一个直接的场景描述，而是需要构思一个解决方案（如回答"是什么"，进行"设计"，或展示"如何解题"）时，你必须先在脑中构想出一个完整、具体、可被视觉化的方案。这个方案将成为你后续描述的基础。然后，当核心画面确立后（无论是直接来自用户还是经过你的推理），你将为其注入专业级的美学与真实感细节。这包括明确构图、设定光影氛围、描述材质质感、定义色彩方案，并构建富有层次感的空间。最后，是对所有文字元素的精确处理，这是至关重要的一步。在画面描述中，当你提到某个元素时，应该将其上的文字一并描述，而不是单独列举。所有需要在画面中呈现的文字，都必须自然地融入画面场景中描述（如：车身标注着"18-30万美元"，屏幕显示"30分钟"，价格牌上写着"千亿美元"），而不是在描述完画面后再单独列出文字清单。你的最终描述必须客观、具象，严禁使用比喻、情感化修辞，也绝不包含"8K"、"杰作"等元标签或绘制指令。最终输出的prompt必须超过500字，以确保画面细节丰富、描述饱满。仅严格输出最终的修改后的prompt，不要输出任何其他内容。用户输入 prompt: {输入内容}"""

# ============== 工具函数 ==============

def call_llm(prompt, max_tokens=2000):
    """调用LLM API - minimax-portal"""
    if not LLM_API_KEY:
        print("警告：未设置MINIMAX_API_KEY环境变量")
        return None
    
    payload = {
        "model": "MiniMax-M2.7",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    cmd = [
        'curl', '-s', '-X', 'POST',
        'https://api.minimaxi.com/anthropic/v1/messages',
        '-H', f'Authorization: Bearer {LLM_API_KEY}',
        '-H', f'x-api-key: {LLM_API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        response = json.loads(result.stdout)
        if 'content' in response:
            # 提取text类型的内容，跳过thinking
            for item in response.get('content', []):
                if item.get('type') == 'text':
                    return item.get('text', '')
            # 如果没有text类型，返回空
            print(f"警告：未找到text类型content")
            return ''
        elif 'error' in response:
            print(f"API错误: {response['error']}")
            return None
        else:
            print(f"未知响应: {str(response)[:200]}")
            return None
    except Exception as e:
        print(f"调用失败: {e}")
        return None

def read_file(file_path):
    """读取文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    """写入文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_slides(content):
    """解析slides内容"""
    slides = []
    current_slide = None
    
    for line in content.split('\n'):
        if line.startswith('### '):
            if current_slide:
                slides.append(current_slide)
            parts = line.split('|')
            if len(parts) >= 2:
                current_slide = {
                    'id': parts[0].replace('###', '').strip(),
                    'title': parts[1].strip()
                }
        elif current_slide:
            if line.startswith('- **逐字稿**：'):
                current_slide['script'] = line.replace('- **逐字稿**：', '').strip()
            elif line.startswith('- **背景知识**：'):
                current_slide['background'] = line.replace('- **背景知识**：', '').strip()
    
    if current_slide:
        slides.append(current_slide)
    
    return slides

def generate_meta_prompt(slide):
    """生成元模板实例化"""
    script = slide.get('script', '')
    background = slide.get('background', '')
    input_content = f"{script}。背景知识：{background}"
    
    return PROMPT_TEMPLATE.format(输入风格=STYLE, 输入内容=input_content)

# ============== 主流程 ==============

def main():
    # 解析参数
    if len(sys.argv) < 2:
        print("用法: python3 gen_prompts.py <项目目录>")
        print("示例: python3 gen_prompts.py ~/.openclaw/workspace-rex/tmp-slides/semi-ev3")
        sys.exit(1)
    
    project_dir = os.path.expanduser(sys.argv[1])
    content_file = os.path.join(project_dir, 'slides_content.md')
    
    print(f"读取slides内容: {content_file}")
    
    # 读取并解析
    content = read_file(content_file)
    slides = parse_slides(content)
    print(f"读取到{len(slides)}张slides\n")
    
    # 输出目录
    prompts_dir = os.path.join(project_dir, 'prompts')
    os.makedirs(prompts_dir, exist_ok=True)
    
    # 处理每张slide
    results = []
    for i, slide in enumerate(slides):
        slide_id = slide['id']
        title = slide['title']
        
        print(f"[{i+1}/{len(slides)}] Slide {slide_id}: {title}")
        
        # 1. 生成元模板实例化
        meta_prompt = generate_meta_prompt(slide)
        print(f"  - 元模板实例化: {len(meta_prompt)}字符")
        
        # 2. 调用LLM执行
        print(f"  - 调用LLM执行...")
        image_prompt = call_llm(meta_prompt, max_tokens=2000)
        
        if image_prompt:
            # 清理输出（移除可能的引号包装）
            image_prompt = image_prompt.strip('"\n ')
            
            print(f"  - 生成提示词: {len(image_prompt)}字符")
            
            # 保存单独文件
            slide_file = os.path.join(prompts_dir, f"slide_{slide_id}.txt")
            write_file(slide_file, image_prompt)
            print(f"  - 已保存: {slide_file}")
            
            results.append({
                'id': slide_id,
                'title': title,
                'prompt': image_prompt,
                'meta_prompt': meta_prompt
            })
        else:
            print(f"  - LLM调用失败，使用元模板实例化")
            results.append({
                'id': slide_id,
                'title': title,
                'prompt': None,
                'meta_prompt': meta_prompt
            })
        
        print()
        time.sleep(1)  # 避免API限流
    
    # 保存汇总文件
    summary_file = os.path.join(prompts_dir, 'prompts_summary.md')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# 图片提示词汇总\n\n")
        for r in results:
            f.write(f"## Slide {r['id']} - {r['title']}\n\n")
            f.write(f"### 元模板实例化\n\n")
            f.write(f"```\n{r['meta_prompt']}\n```\n\n")
            if r['prompt']:
                f.write(f"### 图片提示词 ({len(r['prompt'])}字符)\n\n")
                f.write(f"{r['prompt']}\n\n")
            f.write("---\n\n")
    
    print(f"\n提示词已保存到: {prompts_dir}")
    print(f"汇总文件: {summary_file}")

if __name__ == '__main__':
    main()
