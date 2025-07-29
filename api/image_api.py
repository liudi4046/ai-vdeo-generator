import requests
import json
import base64
import hashlib
import hmac
import urllib.parse
from datetime import datetime
import os
from typing import Optional
from config import IMAGE_API_CONFIG


class ImageAPI:
    """火山引擎文生图API封装类"""
    
    def __init__(self, access_key: str = None, secret_key: str = None):
        """
        初始化文生图API
        
        Args:
            access_key: 访问密钥
            secret_key: 秘密密钥
        """
        self.base_url = IMAGE_API_CONFIG["base_url"]
        self.req_key = IMAGE_API_CONFIG["req_key"]
        self.region = IMAGE_API_CONFIG["region"]
        self.service = IMAGE_API_CONFIG["service"]
        self.action = IMAGE_API_CONFIG["action"]
        self.version = IMAGE_API_CONFIG["version"]
        
        self.access_key = access_key or IMAGE_API_CONFIG["access_key"]
        self.secret_key = secret_key or IMAGE_API_CONFIG["secret_key"]
        
        if not self.access_key or not self.secret_key:
            raise ValueError("访问密钥和秘密密钥未提供，请在环境变量中设置或作为参数传入")
    
    def generate_image(self, prompt: str, output_path: str, 
                      width: int = 1328, height: int = 1328,
                      use_pre_llm: bool = False, scale: float = 2.5) -> bool:
        """
        根据描述生成图像
        
        Args:
            prompt: 图像描述
            output_path: 输出图像文件路径
            width: 图像宽度
            height: 图像高度
            use_pre_llm: 是否开启文本扩写
            scale: 文本描述程度
            
        Returns:
            是否生成成功
        """
        if not prompt.strip():
            return False
        
        # 构建请求参数
        query_params = {
            "Action": self.action,
            "Version": self.version
        }
        
        # 构建请求体
        payload = {
            "req_key": self.req_key,
            "prompt": prompt,
            "width": width,
            "height": height,
            "use_pre_llm": use_pre_llm,
            "scale": scale,
            "return_url": False,  # 直接返回base64数据
            "logo_info": {
                "add_logo": False
            }
        }
        
        try:
            # 生成签名和请求头
            headers = self._generate_headers(query_params, payload)
            
            # 构建完整URL
            url = f"{self.base_url}?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120  # 图像生成可能需要较长时间
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 检查响应状态
            if result.get("code") != 10000:
                error_msg = result.get("message", "未知错误")
                raise Exception(f"图像生成失败: {error_msg}")
            
            # 获取图像数据
            data = result.get("data", {})
            binary_data_base64 = data.get("binary_data_base64")
            
            if binary_data_base64 and len(binary_data_base64) > 0:
                # 解码并保存图像文件
                image_data = base64.b64decode(binary_data_base64[0])
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                return True
            else:
                # 尝试从URL获取图像
                image_urls = data.get("image_urls")
                if image_urls and len(image_urls) > 0:
                    return self._download_image(image_urls[0], output_path)
                else:
                    raise Exception("响应中未找到图像数据")
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"响应解析失败: {e}")
            return False
        except Exception as e:
            print(f"图像生成错误: {e}")
            return False
    
    def _download_image(self, url: str, output_path: str) -> bool:
        """
        从URL下载图像
        
        Args:
            url: 图像URL
            output_path: 输出路径
            
        Returns:
            是否下载成功
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"图像下载失败: {e}")
            return False
    
    def _generate_headers(self, query_params: dict, payload: dict) -> dict:
        """
        生成请求头，包含签名认证
        
        Args:
            query_params: 查询参数
            payload: 请求体
            
        Returns:
            请求头字典
        """
        # 获取当前时间
        now = datetime.utcnow()
        date_stamp = now.strftime('%Y%m%d')
        time_stamp = now.strftime('%Y%m%dT%H%M%SZ')
        
        # 构建请求体字符串
        payload_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
        
        # 计算请求体的哈希值
        payload_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        # 构建规范请求
        canonical_query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(query_params.items())])
        canonical_headers = f"content-type:application/json\nhost:visual.volcengineapi.com\nx-date:{time_stamp}\n"
        signed_headers = "content-type;host;x-date"
        
        canonical_request = f"POST\n/\n{canonical_query_string}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # 构建签名字符串
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{time_stamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        # 计算签名
        signing_key = self._get_signing_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 构建Authorization头
        authorization = f"HMAC-SHA256 Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        return {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "X-Date": time_stamp,
        }
    
    def _get_signing_key(self, date_stamp: str) -> bytes:
        """
        生成签名密钥
        
        Args:
            date_stamp: 日期戳
            
        Returns:
            签名密钥
        """
        k_date = hmac.new(self.secret_key.encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "request".encode('utf-8'), hashlib.sha256).digest()
        return k_signing
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            # 使用一个简单的测试prompt
            test_prompt = "一个简单的测试图像"
            
            query_params = {
                "Action": self.action,
                "Version": self.version
            }
            
            payload = {
                "req_key": self.req_key,
                "prompt": test_prompt,
                "width": 512,
                "height": 512,
                "return_url": True
            }
            
            headers = self._generate_headers(query_params, payload)
            url = f"{self.base_url}?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("code") == 10000
            
            return False
            
        except Exception:
            return False 