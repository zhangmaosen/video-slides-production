#!/usr/bin/env python3
"""
ComfyUI API 客户端 - Qwen-Image 图像生成
基于实际 ComfyUI 工作流配置
参考：https://github.com/Comfy-Org/ComfyUI/blob/master/script_examples/basic_api_example.py
"""

import json
import time
import uuid
from urllib import request
from typing import Optional, Dict, Any

class ComfyUIAPI:
    """ComfyUI API 客户端"""
    
    def __init__(self, base_url: str = "http://100.111.221.7:8188"):
        self.base_url = base_url.rstrip('/')
        self.client_id = str(uuid.uuid4())
        
    def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """提交生成任务（参考官方示例）"""
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = request.Request(f"{self.base_url}/prompt", data=data)
        
        try:
            response = request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))
            return result
        except Exception as e:
            print(f"❌ 请求失败：{e}")
            return {"error": {"message": str(e)}}
    
    def get_history(self) -> Dict[str, Any]:
        """获取所有历史记录"""
        try:
            response = request.urlopen(f"{self.base_url}/history")
            return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"❌ 获取历史失败：{e}")
            return {}
    
    def get_queue(self) -> Dict[str, Any]:
        """获取队列状态"""
        try:
            response = request.urlopen(f"{self.base_url}/queue")
            return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"❌ 获取队列失败：{e}")
            return {}
    
    def generate_image(
        self,
        prompt_text: str,
        negative_prompt: str = "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲",
        width: int = 1328,
        height: int = 1328,
        seed: Optional[int] = None,
        use_lightning: bool = False,
        filename_prefix: str = "Qwen-Image-2512"
    ) -> Dict[str, Any]:
        """
        生成图像（基于实际 ComfyUI 工作流）
        
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
        
        # 构建完整工作流（基于实际 ComfyUI 工作流）
        workflow = {
            # 60. 保存图像
            "60": {
                "inputs": {
                    "filename_prefix": filename_prefix,
                    "images": ["238:231", 0]
                },
                "class_type": "SaveImage"
            },
            # 238:219. 加载 CLIP
            "238:219": {
                "inputs": {
                    "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                    "type": "qwen_image",
                    "device": "default"
                },
                "class_type": "CLIPLoader"
            },
            # 238:220. 加载 VAE
            "238:220": {
                "inputs": {
                    "vae_name": "qwen_image_vae.safetensors"
                },
                "class_type": "VAELoader"
            },
            # 238:226. 加载 UNET
            "238:226": {
                "inputs": {
                    "unet_name": "qwen_image_2512_fp8_e4m3fn.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader"
            },
            # 238:229. Lightning 开关
            "238:229": {
                "inputs": {
                    "value": use_lightning
                },
                "class_type": "PrimitiveBoolean"
            },
            # 238:221. 加载 Lightning LoRA
            "238:221": {
                "inputs": {
                    "lora_name": "Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors",
                    "strength_model": 1,
                    "model": ["238:226", 0]
                },
                "class_type": "LoraLoaderModelOnly"
            },
            # 238:224. 标准模式 Steps
            "238:224": {
                "inputs": {
                    "value": 50
                },
                "class_type": "PrimitiveInt"
            },
            # 238:223. 标准模式 CFG
            "238:223": {
                "inputs": {
                    "value": 4
                },
                "class_type": "PrimitiveFloat"
            },
            # 238:225. Lightning 模式 Steps
            "238:225": {
                "inputs": {
                    "value": 4
                },
                "class_type": "PrimitiveInt"
            },
            # 238:218. Lightning 模式 CFG
            "238:218": {
                "inputs": {
                    "value": 1
                },
                "class_type": "PrimitiveFloat"
            },
            # 238:233. 模型切换
            "238:233": {
                "inputs": {
                    "switch": ["238:229", 0],
                    "on_false": ["238:226", 0],
                    "on_true": ["238:221", 0]
                },
                "class_type": "ComfySwitchNode"
            },
            # 238:240. Steps 切换
            "238:240": {
                "inputs": {
                    "switch": ["238:229", 0],
                    "on_false": ["238:224", 0],
                    "on_true": ["238:225", 0]
                },
                "class_type": "ComfySwitchNode"
            },
            # 238:243. CFG 切换
            "238:243": {
                "inputs": {
                    "switch": ["238:229", 0],
                    "on_false": ["238:223", 0],
                    "on_true": ["238:218", 0]
                },
                "class_type": "ComfySwitchNode"
            },
            # 238:222. 模型采样
            "238:222": {
                "inputs": {
                    "shift": 3.1,
                    "model": ["238:233", 0]
                },
                "class_type": "ModelSamplingAuraFlow"
            },
            # 238:227. 正提示词
            "238:227": {
                "inputs": {
                    "text": prompt_text,
                    "clip": ["238:219", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            # 238:228. 负提示词
            "238:228": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["238:219", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            # 238:232. 空潜空间
            "238:232": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptySD3LatentImage"
            },
            # 238:230. KSampler
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
            # 238:231. VAE 解码
            "238:231": {
                "inputs": {
                    "samples": ["238:230", 0],
                    "vae": ["238:220", 0]
                },
                "class_type": "VAEDecode"
            }
        }
        
        # 提交任务
        result = self.queue_prompt(workflow)
        prompt_id = result.get("prompt_id")
        
        if prompt_id:
            print(f"✅ 任务已提交：{prompt_id}")
            print(f"   模式：{'Lightning (4 步)' if use_lightning else '标准 (50 步)'}")
            print(f"   分辨率：{width}x{height}")
            print(f"   种子：{seed}")
        else:
            print(f"❌ 任务提交失败：{result}")
        
        return {
            "prompt_id": prompt_id,
            "seed": seed,
            "use_lightning": use_lightning,
            "status": "queued" if prompt_id else "failed",
            "error": result.get("error") if not prompt_id else None
        }


# 使用示例
if __name__ == "__main__":
    api = ComfyUIAPI()
    
    # 示例 1：标准模式生成
    result = api.generate_image(
        prompt_text="一辆绿色的特斯拉 Semi 卡车",
        use_lightning=False,
        filename_prefix="test_semi_standard"
    )
    print(f"\n标准模式结果：{result}")
    
    # 示例 2：Lightning 模式生成
    result = api.generate_image(
        prompt_text="一辆绿色的特斯拉 Semi 卡车",
        use_lightning=True,
        filename_prefix="test_semi_lightning"
    )
    print(f"\nLightning 模式结果：{result}")
