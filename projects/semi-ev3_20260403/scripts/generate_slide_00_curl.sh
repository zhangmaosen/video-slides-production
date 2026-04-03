#!/bin/bash
# 使用 curl 调用 ComfyUI API 生成 slide_00

COMFYUI_URL="http://100.111.221.7:8188"
PROMPT_FILE="prompts/slide_00_final.txt"
WORKFLOW_FILE="/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json"

# 读取 prompt
PROMPT=$(cat $PROMPT_FILE)

echo "=========================================="
echo "生成 slide_00 图片"
echo "=========================================="
echo "Prompt: $PROMPT"
echo ""

# 使用 Python 脚本调用 ComfyUI API
python3 << PYEOF
import sys
sys.path.append('/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts')
from comfyui_api import ComfyUIQwenImageAPI

# 读取 prompt
with open('$PROMPT_FILE', 'r', encoding='utf-8') as f:
    prompt = f.read()

# 初始化 API
api = ComfyUIQwenImageAPI("$COMFYUI_URL")

# 生成图片（Lightning 模式）
result = api.generate_image(
    prompt_text=prompt,
    negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲",
    width=1664,
    height=928,
    seed=None,
    use_lightning=True,
    filename_prefix="slide_00"
)

print(f"\n结果：{result}")
PYEOF
