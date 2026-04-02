#!/usr/bin/env python3
"""测试规则解析"""
import re
import json

with open('CONDITION_RULES.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 按规则块分割
rules = {}

# 找到所有规则的开始位置
rule_starts = []
for match in re.finditer(r'### 规则 (\w+)[::]([^\n]+)', content):
    rule_id = match.group(1)
    rule_name = match.group(2).strip()
    start = match.start()
    rule_starts.append((rule_id, rule_name, start))

print(f"找到 {len(rule_starts)} 个规则")

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
            try:
                keywords = json.loads(keywords_str)
            except:
                keywords = [k.strip().strip('"\'') for k in keywords_str.replace('[', '').replace(']', '').split(',')]
        else:
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
    
    print(f"\n规则 {rule_id}: {rule_name}")
    print(f"  关键词：{keywords}")
    print(f"  描述：{description[:50]}...")

print(f"\n\n总共加载 {len(rules)} 个规则")
