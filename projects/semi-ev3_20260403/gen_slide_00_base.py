#!/usr/bin/env python3
import os, sys, json, random, time, requests
from pathlib import Path

API_URL = "http://100.111.221.7:8188"
WORKFLOW_PATH = Path("/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/ComfyUI/Qwen-Image-2512_ComfyUI.json")
PROJECT_DIR = Path(__file__).parent
OUTPUT_PATH = PROJECT_DIR / "slides" / "slide_00_base_v1.png"

# Read prompts
positive_file = PROJECT_DIR / "prompts" / "slide_00_positive.txt"
negative_file = PROJECT_DIR / "prompts" / "slide_00_negative.txt"

with open(positive_file, 'r', encoding='utf-8') as f:
    positive_prompt = f.read().strip()

with open(negative_file, 'r', encoding='utf-8') as f:
    negative_prompt = f.read().strip()

print(f"Positive prompt: {len(positive_prompt)} chars")
print(f"Negative prompt: {len(negative_prompt)} chars")

# Load workflow
with open(WORKFLOW_PATH, 'r') as f:
    workflow = json.load(f)

seed = random.randint(0, 2**32 - 1)
print(f"Seed: {seed}")

# Modify workflow nodes
for node_id, node in workflow.items():
    cls = node.get('class_type', '')
    inputs = node.get('inputs', {})

    if cls == 'CLIPTextEncode':
        text = inputs.get('text', '')
        if 'negative' in str(node_id).lower() or 'neg' in str(node_id).lower():
            inputs['text'] = negative_prompt
            print(f"  Node {node_id}: set negative prompt")
        else:
            inputs['text'] = positive_prompt
            print(f"  Node {node_id}: set positive prompt")
    elif cls == 'EmptySD3LatentImage':
        inputs['width'] = 1280
        inputs['height'] = 800
        inputs['seed'] = seed
        print(f"  Node {node_id}: set size 1280x800, seed={seed}")
    elif cls == 'KSampler':
        inputs['steps'] = 50
        inputs['cfg'] = 4
        print(f"  Node {node_id}: set steps=50, cfg=4")

# Submit job
data = {"prompt": workflow}
print("Submitting to ComfyUI...")
resp = requests.post(f"{API_URL}/prompt", json=data, timeout=30)
result = resp.json()
task_id = result.get('prompt_id')
print(f"Task ID: {task_id}")

if not task_id:
    print(f"Failed: {result}")
    sys.exit(1)

# Wait for completion
max_wait = 300
start = time.time()
while time.time() - start < max_wait:
    history = requests.get(f"{API_URL}/history/{task_id}", timeout=10).json()
    if task_id in history:
        outputs = history[task_id].get('outputs', {})
        for nid, nout in outputs.items():
            if 'images' in nout:
                for img in nout['images']:
                    fn = img['filename']
                    img_resp = requests.get(f"{API_URL}/view?filename={fn}", timeout=30)
                    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with open(OUTPUT_PATH, 'wb') as f:
                        f.write(img_resp.content)
                    size = len(img_resp.content)
                    print(f"✓ Saved: {OUTPUT_PATH} ({size} bytes)")
        print("Done!")
        sys.exit(0)
    time.sleep(3)
    print(f"  Waiting... ({int(time.time()-start)}s)")

print("Timeout!")
sys.exit(1)
