import requests
import json
import base64
import uuid
import os
from typing import Optional
from config import TTS_API_CONFIG


class TTSAPI:
    """火山引擎语音合成API封装类"""
    
    def __init__(self):
        """初始化语音合成API"""
        self.http_url = TTS_API_CONFIG["http_url"]
        self.app_id = TTS_API_CONFIG["app_id"]
        self.access_token = TTS_API_CONFIG["access_token"]
        self.voice_type = TTS_API_CONFIG["voice_type"]
        self.cluster = TTS_API_CONFIG["cluster"]
    
    def text_to_speech(self, text: str, output_path: str, voice_type: str = None) -> bool:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
            voice_type: 音色类型，如果不指定则使用默认音色
            
        Returns:
            是否转换成功
        """
        if not text.strip():
            return False
        
        # 生成唯一的请求ID
        req_id = str(uuid.uuid4())
        
        # 使用指定的音色或默认音色
        selected_voice_type = voice_type or self.voice_type
        
        # 构建请求数据
        payload = {
            "app": {
                "appid": self.app_id,
                "token": "fake_token",  # 文档中说明这是fake token
                "cluster": self.cluster
            },
            "user": {
                "uid": "user_001"
            },
            "audio": {
                "voice_type": selected_voice_type,
                "encoding": "wav",
                "speed_ratio": 1.0,
                "rate": 24000,
                "loudness_ratio": 1.0
            },
            "request": {
                "reqid": req_id,
                "text": text,
                "operation": "query"
            }
        }
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.access_token}"
        }
        
        try:
            response = requests.post(
                self.http_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 检查响应状态
            if result.get("code") != 3000:
                error_msg = result.get("message", "未知错误")
                raise Exception(f"语音合成失败: {error_msg}")
            
            # 获取音频数据
            audio_data_base64 = result.get("data")
            if not audio_data_base64:
                raise Exception("响应中未找到音频数据")
            
            # 解码并保存音频文件
            audio_data = base64.b64decode(audio_data_base64)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {e}")
            return False
        except Exception as e:
            print(f"语音合成错误: {e}")
            return False
    
    def get_available_voices(self) -> list:
        """
        获取可用的音色列表
        
        Returns:
            音色列表
        """
        # 常用的中文音色列表（基于文档中的示例）
        return [
            "zh_female_cancan_mars_bigtts",  # 女声
            "zh_male_M392_conversation_wvae_bigtts",  # 男声
            "zh_female_xinyi_mars_bigtts",  # 女声（心怡）
            "zh_male_yanzi_mars_bigtts",  # 男声（燕子）
        ]
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            # 使用一个简短的测试文本
            test_text = "测试"
            req_id = str(uuid.uuid4())
            
            payload = {
                "app": {
                    "appid": self.app_id,
                    "token": "fake_token",
                    "cluster": self.cluster
                },
                "user": {
                    "uid": "test_user"
                },
                "audio": {
                    "voice_type": self.voice_type,
                    "encoding": "wav"
                },
                "request": {
                    "reqid": req_id,
                    "text": test_text,
                    "operation": "query"
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer;{self.access_token}"
            }
            
            response = requests.post(
                self.http_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("code") == 3000
            
            return False
            
        except Exception:
            return False
    
    def estimate_duration(self, text: str, speech_rate: float = 1.0) -> float:
        """
        估算文本的朗读时间
        
        Args:
            text: 文本内容
            speech_rate: 语速倍率
            
        Returns:
            估算的朗读时间（秒）
        """
        # 中文平均语速约为每分钟200-250字，这里按照220字/分钟计算
        chars_per_minute = 220
        char_count = len(text)
        duration_minutes = char_count / chars_per_minute
        duration_seconds = duration_minutes * 60 / speech_rate
        
        # 加上一些缓冲时间
        return max(duration_seconds + 1, 2)  # 最少2秒 