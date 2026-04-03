#!/bin/bash
cd /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403
python3 /Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/scripts/batch_generate_prompts_local.py --project projects/semi-ev3_20260403 --content-file slides_content.json --output-dir prompts --style "混子说手绘 + 硬核工程拆解爆炸图风格，线条粗细变化，诙谐严肃混合，技术细节清晰，结构透视感强，舞台感构图"
