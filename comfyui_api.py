#!/usr/bin/env python3
"""
ComfyUI API 客户端 - Qwen-Image 图像生成和编辑
支持：
- 文本到图像生成（Lightning 模式）
- 图像编辑（绿身替换）
"""

import requests
import json
import time
import uuid
from typing import Optional, Dict, Any

class ComfyUIAPI:
    """ComfyUI API 客户端"""
    
    def __init__(self, base_url: str = "http://100.111.221.7:8188"):
        self.base_url = base_url.rstrip('/')
        self.client_id = str(uuid.uuid4())
        
    def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """提交生成任务"""
        prompt["client_id"] = self.client_id
        response = requests.post(f"{self.base_url}/prompt", json=prompt)
        result = response.json()
        return result
    
    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """获取生成历史"""
        response = requests.get(f"{self.base_url}/history/{prompt_id}")
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """获取 ComfyUI 状态"""
        response = requests.get(f"{self.base_url}/queue")
        return response.json()
    
    def generate_image(
        self,
        prompt_text: str,
        negative_prompt: str = "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲",
        width: int = 1280,
        height: int = 800,
        seed: Optional[int] = None,
        use_lightning: bool = True,
        filename_prefix: str = "Qwen-Image"
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt_text: 正提示词
            negative_prompt: 负提示词
            width: 图像宽度
            height: 图像高度
            seed: 随机种子（None 表示随机）
            use_lightning: 是否使用 Lightning 模式（4 步快速生成）
            filename_prefix: 输出文件名前缀
            
        Returns:
            生成结果
        """
        if seed is None:
            seed = int(time.time() * 1000000) % (2**32)
        
        # Lightning 模式参数
        if use_lightning:
            steps = 4
            cfg = 1
            lora_enabled = True
        else:
            steps = 50
            cfg = 4
            lora_enabled = False
        
        # 构建工作流
        workflow = {
            "238:232": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptySD3LatentImage"
            },
            "238:229": {
                "inputs": {
                    "value": lora_enabled
                },
                "class_type": "PrimitiveBoolean"
            },
            "238:227": {
                "inputs": {
                    "text": prompt_text,
                    "clip": ["238:219", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "238:228": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["238:219", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "238:230": {
                "inputs": {
                    "seed": seed,
                    "steps": ["238:240", 0],
                    "cfg": ["238:243", 0],
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["238:222", 0],
                    "positive": ["238:227", 0],
                    "negative": ["238:228", 0],
                    "latent_image": ["238:232", 0]
                },
                "class_type": "KSampler"
            },
            "238:231": {
                "inputs": {
                    "samples": ["238:230", 0],
                    "vae": ["238:220", 0]
                },
                "class_type": "VAEDecode"
            },
            "60": {
                "inputs": {
                    "filename_prefix": filename_prefix,
                    "images": ["238:231", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        # 提交任务
        result = self.queue_prompt(workflow)
        prompt_id = result.get("prompt_id")
        
        print(f"✅ 任务已提交：{prompt_id}")
        print(f"   模式：{'Lightning (4 步)' if use_lightning else '标准 (50 步)'}")
        print(f"   分辨率：{width}x{height}")
        print(f"   种子：{seed}")
        
        return {
            "prompt_id": prompt_id,
            "seed": seed,
            "use_lightning": use_lightning,
            "status": "queued"
        }
    
    def edit_image(
        self,
        source_image_path: str,
        reference_image_path: str,
        edit_prompt: str = "把图 1 中的绿色卡车改成图 2 的卡车",
        seed: Optional[int] = None,
        filename_prefix: str = "Qwen-Image-Edit"
    ) -> Dict[str, Any]:
        """
        图像编辑（绿身替换）
        
        Args:
            source_image_path: 源图像路径（包含绿色卡车）
            reference_image_path: 参考图像路径（目标卡车）
            edit_prompt: 编辑提示词
            seed: 随机种子
            filename_prefix: 输出文件名前缀
            
        Returns:
            编辑结果
        """
        if seed is None:
            seed = int(time.time() * 1000000) % (2**32)
        
        # 构建编辑工作流
        workflow = {
            "437": {
                "inputs": {
                    "image": reference_image_path
                },
                "class_type": "LoadImage"
            },
            "436:111": {
                "inputs": {
                    "prompt": edit_prompt,
                    "clip": ["436:38", 0],
                    "vae": ["436:39", 0],
                    "image1": ["436:117", 0],
                    "image2": ["437", 0]
                },
                "class_type": "TextEncodeQwenImageEditPlus"
            },
            "436:3": {
                "inputs": {
                    "seed": seed,
                    "steps": 4,
                    "cfg": 1,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["436:75", 0],
                    "positive": ["436:111", 0],
                    "negative": ["436:110", 0],
                    "latent_image": ["436:88", 0]
                },
                "class_type": "KSampler"
            },
            "436:8": {
                "inputs": {
                    "samples": ["436:3", 0],
                    "vae": ["436:39", 0]
                },
                "class_type": "VAEDecode"
            },
            "60": {
                "inputs": {
                    "filename_prefix": filename_prefix,
                    "images": ["436:8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        # 提交任务
        result = self.queue_prompt(workflow)
        prompt_id = result.get("prompt_id")
        
        print(f"✅ 编辑任务已提交：{prompt_id}")
        print(f"   源图像：{source_image_path}")
        print(f"   参考图像：{reference_image_path}")
        print(f"   提示词：{edit_prompt}")
        
        return {
            "prompt_id": prompt_id,
            "seed": seed,
            "status": "queued"
        }
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            prompt_id: 任务 ID
            timeout: 超时时间（秒）
            
        Returns:
            完成状态和输出图像路径
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                return {"status": "timeout", "error": "任务超时"}
            
            history = self.get_history(prompt_id)
            
            if prompt_id in history:
                task = history[prompt_id]
                outputs = task.get("outputs", {})
                
                # 查找 SaveImage 节点的输出
                for node_id, node_outputs in outputs.items():
                    if "images" in node_outputs:
                        images = node_outputs["images"]
                        image_paths = [img["filename"] for img in images]
                        return {
                            "status": "completed",
                            "images": image_paths
                        }
            
            time.sleep(2)


# 使用示例
if __name__ == "__main__":
    api = ComfyUIAPI()
    
    # 示例 1：生成图像
    result = api.generate_image(
        prompt_text="一辆绿色的卡车",
        use_lightning=True,
        filename_prefix="test_green_truck"
    )
    print(f"生成结果：{result}")
    
    # 示例 2：编辑图像
    # result = api.edit_image(
    #     source_image_path="green_truck.png",
    #     reference_image_path="reference_truck.png",
    #     edit_prompt="把图 1 中的绿色卡车改成图 2 的卡车"
    # )
    # print(f"编辑结果：{result}")
