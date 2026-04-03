#!/bin/bash
# 使用 curl 调用 ComfyUI API 生成 slide_00 v2

COMFYUI_URL="http://100.111.221.7:8188"
PROMPT_FILE="prompts/slide_00_positive_v2.txt"
NEGATIVE_FILE="prompts/slide_00_negative_v2.txt"

# 读取 prompt
PROMPT=$(cat $PROMPT_FILE)
NEGATIVE=$(cat $NEGATIVE_FILE)

echo "=========================================="
echo "生成 slide_00 v2 图片"
echo "=========================================="
echo "Prompt: $PROMPT"
echo ""
echo "Negative: $NEGATIVE"
echo ""

# 使用 Python 脚本调用 ComfyUI API
python3 << PYEOF
import sys
sys.path.append('/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts')
from comfyui_api import ComfyUIQwenImageAPI

# 读取 prompt
with open('$PROMPT_FILE', 'r', encoding='utf-8') as f:
    prompt = f.read()

with open('$NEGATIVE_FILE', 'r', encoding='utf-8') as f:
    negative = f.read()

# 初始化 API
api = ComfyUIQwenImageAPI("$COMFYUI_URL")

# 生成图片（Lightning 模式）
result = api.generate_image(
    prompt_text=prompt,
    negative_prompt=negative,
    width=1664,
    height=928,
    seed=None,
    use_lightning=True,
    filename_prefix="slide_00_v2"
)

print(f"\n结果：{result}")
PYEOF
