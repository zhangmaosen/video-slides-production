#!/usr/bin/env python3
"""
批量生成图片提示词 - 通用脚本
使用元提示词模板 + 条件规则配置 + 项目内容
"""
import subprocess
import json
import os
import sys
import argparse

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # skills 的上级目录是 workspace

def load_meta_template(template_path):
    """加载元提示词模板"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_condition_rules(rules_path):
    """加载条件规则配置"""
    import re
    
    rules = {}
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有规则的开始位置
    rule_starts = []
    for match in re.finditer(r'### 规则 (\w+)(:|：)([^\n]+)', content):
        rule_id = match.group(1)
        rule_name = match.group(3).strip()
        start = match.start()
        rule_starts.append((rule_id, rule_name, start))
    
    # 解析每个规则块
    for i, (rule_id, rule_name, start) in enumerate(rule_starts):
        # 找到下一个规则的起始位置（或文件末尾）
        if i + 1 < len(rule_starts):
            end = rule_starts[i + 1][2]
        else:
            end = len(content)
        
        rule_content = content[start:end]
        
        # 提取关键词
        keyword_match = re.search(r'\*\*触发关键词\*\*：`([^`]+)`', rule_content)
        if keyword_match:
            keywords_str = keyword_match.group(1).strip()
            if keywords_str.startswith('['):
                # JSON 数组格式：["semi", "Semi"]
                try:
                    keywords = json.loads(keywords_str)
                except:
                    keywords = [k.strip().strip('"\'') for k in keywords_str.replace('[', '').replace(']', '').split(',')]
            else:
                # 逗号分隔：semi, Semi
                keywords = [k.strip() for k in keywords_str.split(',')]
        else:
            keywords = []
        
        # 提取描述内容
        desc_match = re.search(r'\*\*描述内容\*\*：\n\n```([\s\S]*?)```', rule_content)
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            description = ""
        
        rules[rule_id] = {
            'name': rule_name,
            'keywords': keywords,
            'description': description
        }
    
    return rules

def check_triggers(input_content, rules):
    """根据输入内容检查触发了哪些规则"""
    triggered = []
    content_lower = input_content.lower()
    
    for rule_id, rule in rules.items():
        for keyword in rule['keywords']:
            if keyword.lower() in content_lower:
                triggered.append(rule)
                break
    
    return triggered

def build_prompt(meta_template, style, title, viewpoint, script, background, triggered_rules):
    """构建完整的提示词"""
    
    # 将触发的规则格式化为 markdown
    rules_text = ""
    if triggered_rules:
        for rule in triggered_rules:
            rules_text += f"### {rule['name']}\\n"
            rules_text += f"{rule['description']}\\n\\n"
    
    # 在元模板中注入规则
    if "## 条件规则注入" in meta_template:
        inject_marker = "## 条件规则注入"
        insert_pos = meta_template.find(inject_marker)
        next_section = meta_template.find("\\n---\\n\\n## 输出格式", insert_pos)
        if next_section > 0:
            # 如果触发了 Tesla Semi 规则，添加明确的指令
            special_instruction = ""
            if triggered_rules:
                for rule in triggered_rules:
                    if "Tesla Semi" in rule['name']:
                        special_instruction = "**特别注意**：在描述 Tesla Semi 时，必须使用电动半挂重型卡车这个产品类型描述，不能只用特斯拉 Semi 代替！\n\n"
                        break
            
            rules_injection = f"\\n---\\n\\n## 本次生成触发的条件规则\\n\\n{special_instruction}**重要**：在生成提示词时，必须将以下规则描述自然融入画面中，不要单独列出或标注重要：\\n\\n{rules_text}\\n---\\n\\n"
            meta_template = meta_template[:next_section] + rules_injection + meta_template[next_section:]
    
    # 替换用户输入
    if "{输入风格}" in meta_template:
        meta_template = meta_template.replace("{输入风格}", style)
    
    # 构建用户输入部分
    # 如果触发了 Tesla Semi 规则，在背景知识中添加产品类型说明
    background_with_type = background
    if triggered_rules:
        for rule in triggered_rules:
            if "Tesla Semi" in rule['name']:
                background_with_type = f"电动半挂重型卡车。{background}"
                break
    
    user_input = f"""
- 视觉风格：{style}
- 标题：{title}
- 观点：{viewpoint}
- 逐字稿：{script}
- 背景知识：{background_with_type}
"""
    
    # 如果模板中有用户输入占位符，替换它
    if "{用户输入}" in meta_template:
        meta_template = meta_template.replace("{用户输入}", user_input)
    else:
        # 否则追加到末尾
        meta_template += f"\\n---\\n\\n# 用户输入\\n{user_input}"
    
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
    
    # 元模板和规则配置路径
    meta_template_path = os.path.join(SCRIPT_DIR, 'META_PROMPT.md')
    condition_rules_path = os.path.join(SCRIPT_DIR, 'CONDITION_RULES.md')
    
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
    print(f"条件规则：{condition_rules_path}")
    print(f"输出目录：{output_dir}")
    print()
    
    # 加载元模板
    print("正在加载元提示词模板...")
    meta_template = load_meta_template(meta_template_path)
    print(f"  ✓ 元模板已加载 ({len(meta_template)} 字符)")
    
    # 加载条件规则
    print("正在加载条件规则配置...")
    rules = load_condition_rules(condition_rules_path)
    print(f"  ✓ 条件规则已加载 ({len(rules)} 个规则)")
    
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
            # 检查触发的规则
            input_content = slide_data.get('script', '') + slide_data.get('background', '')
            triggered_rules = check_triggers(input_content, rules)
            
            # 构建提示词
            prompt = build_prompt(
                meta_template,
                args.style,
                slide_data.get('title', ''),
                slide_data.get('viewpoint', ''),
                slide_data.get('script', ''),
                slide_data.get('background', ''),
                triggered_rules
            )
            
            # 调用 API
            content = generate_prompt(api_key, args.api_url, args.model, prompt)
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ 已保存 ({len(content)} 字符)")
            print(f"    触发规则：{len(triggered_rules)} 个")
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
