#!/usr/bin/env python3
"""Download result for a given prompt_id"""
import json
import urllib.request
import urllib.error
import os
import sys
import time

API_URL = "http://100.111.221.7:8188"
OUTPUT_DIR = "/Users/maosen/.openclaw/workspace-rex/skills/video-slides-production/projects/semi-ev3_20260403/slides"

def download_result(prompt_id, output_filename, max_wait=900):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        time.sleep(10)
        try:
            history_req = urllib.request.Request(f"{API_URL}/history/{prompt_id}", headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(history_req, timeout=30) as hist_resp:
                history = json.loads(hist_resp.read().decode('utf-8'))
            if prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                for node_id, node_output in outputs.items():
                    if 'images' in node_output:
                        for img_info in node_output['images']:
                            filename = img_info['filename']
                            subfolder = img_info.get('subfolder', '')
                            image_url = f"{API_URL}/view?filename={filename}&subfolder={subfolder}"
                            with urllib.request.urlopen(image_url, timeout=60) as img_resp:
                                image_data = img_resp.read()
                            os.makedirs(OUTPUT_DIR, exist_ok=True)
                            output_path = os.path.join(OUTPUT_DIR, output_filename)
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            elapsed = time.time() - start_time
                            print(f"DONE|{output_path}|{elapsed:.1f}s", flush=True)
                            return {"status": "success", "path": output_path, "elapsed": elapsed}
        except Exception as e:
            print(f"WAIT|{e}", flush=True)
            time.sleep(5)
    print(f"TIMEOUT", flush=True)
    return {"status": "error", "error": "Timeout"}

if __name__ == "__main__":
    prompt_id = sys.argv[1]
    output_file = sys.argv[2]
    result = download_result(prompt_id, output_file)
    print(result)
