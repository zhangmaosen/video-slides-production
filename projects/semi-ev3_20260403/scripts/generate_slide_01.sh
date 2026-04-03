#!/bin/bash
# 生成 slide_01 图片

cd /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403

echo "============================================================"
echo "生成 slide_01 图片"
echo "============================================================"

# 生成随机 seed
SEED=$(python3 -c "import random; print(random.randint(0, 2**32-1))")
echo "🎲 Seed: $SEED"

# 读取提示词（转义引号）
POSITIVE=$(cat prompts/slide_01_positive.txt | tr '\n' ' ' | sed 's/"/\\"/g')
NEGATIVE=$(cat prompts/slide_01_negative.txt | tr '\n' ' ' | sed 's/"/\\"/g')

echo "✅ 正向提示词长度：${#POSITIVE}"
echo "✅ 负向提示词长度：${#NEGATIVE}"
echo "📐 分辨率：1280x800, Steps: 50, CFG: 4"
echo "🚀 发送请求到 ComfyUI..."

# 发送请求
RESPONSE=$(curl -s -X POST http://100.111.221.7:8188/prompt \
  -H "Content-Type: application/json" \
  -d "{
    \"3\": {
      \"inputs\": {
        \"seed\": $SEED,
        \"steps\": 50,
        \"cfg\": 4,
        \"sampler_name\": \"euler\",
        \"scheduler\": \"normal\",
        \"denoise\": 1,
        \"model\": [\"4\", 0],
        \"positive\": [\"6\", 0],
        \"negative\": [\"7\", 0],
        \"latent_image\": [\"5\", 0]
      },
      \"class_type\": \"KSampler\"
    },
    \"4\": {
      \"inputs\": {
        \"ckpt_name\": \"qwen_image_2512_fp8_e4m3fn.safetensors\"
      },
      \"class_type\": \"CheckpointLoaderSimple\"
    },
    \"5\": {
      \"inputs\": {
        \"width\": 1280,
        \"height\": 800,
        \"batch_size\": 1
      },
      \"class_type\": \"EmptyLatentImage\"
    },
    \"6\": {
      \"inputs\": {
        \"text\": \"$POSITIVE\",
        \"clip\": [\"4\", 1]
      },
      \"class_type\": \"CLIPTextEncode\"
    },
    \"7\": {
      \"inputs\": {
        \"text\": \"$NEGATIVE\",
        \"clip\": [\"4\", 1]
      },
      \"class_type\": \"CLIPTextEncode\"
    },
    \"8\": {
      \"inputs\": {
        \"samples\": [\"3\", 0],
        \"vae\": [\"4\", 2]
      },
      \"class_type\": \"VAEDecode\"
    },
    \"9\": {
      \"inputs\": {
        \"filename_prefix\": \"slide_01\",
        \"images\": [\"8\", 0]
      },
      \"class_type\": \"SaveImage\"
    }
  }")

PROMPT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', 'unknown'))")
echo "✅ Prompt ID: $PROMPT_ID"
echo "⏳ 等待生成完成..."

# 等待生成
START_TIME=$(date +%s)
MAX_WAIT=300

while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))
  
  if [ $ELAPSED -gt $MAX_WAIT ]; then
    echo "❌ 超时！生成失败"
    exit 1
  fi
  
  HISTORY=$(curl -s "http://100.111.221.7:8188/history/$PROMPT_ID")
  
  # 检查是否有输出
  FILENAME=$(echo $HISTORY | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if '$PROMPT_ID' in data:
        images = data['$PROMPT_ID'].get('outputs', {}).get('9', {}).get('images', [])
        if images:
            print(images[0].get('filename', ''))
except:
    pass
" 2>/dev/null)
  
  if [ -n "$FILENAME" ]; then
    echo "📥 下载图片：$FILENAME"
    
    # 下载图片
    curl -o slides/slide_01.png "http://100.111.221.7:8188/view?filename=$FILENAME"
    
    END_TIME=$(date +%s)
    TOTAL_TIME=$((END_TIME - START_TIME))
    
    echo "✅ 完成！耗时 ${TOTAL_TIME}s"
    echo "📁 保存到：slides/slide_01.png"
    
    echo ""
    echo "📊 结果："
    echo "  - 状态：成功"
    echo "  - 文件名：slide_01.png"
    echo "  - Prompt ID: $PROMPT_ID"
    echo "  - Seed: $SEED"
    echo "  - 耗时：${TOTAL_TIME}s"
    
    break
  fi
  
  sleep 2
done
