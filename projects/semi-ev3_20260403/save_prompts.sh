#!/bin/bash
# 保存所有生成的 prompt 到 final 目录
cd /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403/prompts
for i in {00..17}; do
    if [ -f "slide_${i}_final.txt" ]; then
        echo "✓ slide_${i} 已保存"
    else
        echo "⏳ slide_${i} 待保存"
    fi
done
echo "---"
ls -la *_final.txt 2>/dev/null | wc -l
echo "个 prompt 已保存"
