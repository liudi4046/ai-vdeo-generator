import requests
import json
import re
from typing import List, Dict, Any
from config import CHAT_API_CONFIG, SCRIPT_GENERATION_PROMPT


class ChatAPI:
    """火山引擎对话API封装类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化对话API
        
        Args:
            api_key: API密钥，如果不提供则从环境变量获取
        """
        self.base_url = CHAT_API_CONFIG["base_url"]
        self.model_id = CHAT_API_CONFIG["model_id"]
        self.api_key = api_key or CHAT_API_CONFIG["api_key"]
        
        if not self.api_key:
            raise ValueError("API密钥未提供，请在环境变量ARK_API_KEY中设置或作为参数传入")
    
    def generate_script(self, english_text: str) -> List[Dict[str, Any]]:
        """
        根据英文文本生成中文视频脚本
        
        Args:
            english_text: 输入的英文文本
            
        Returns:
            包含分镜信息的列表
        """
        prompt = SCRIPT_GENERATION_PROMPT.format(english_text=english_text)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 解析JSON响应
            return self._parse_script_response(content)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败: {e}")
        except KeyError as e:
            raise Exception(f"响应格式错误: {e}")
    
    def _parse_script_response(self, content: str) -> List[Dict[str, Any]]:
        """
        解析API响应中的脚本内容
        
        Args:
            content: API返回的内容
            
        Returns:
            解析后的分镜列表
        """
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有代码块，尝试直接解析整个内容
                json_str = content
            
            # 解析JSON
            script_data = json.loads(json_str)
            
            if "scenes" in script_data:
                return script_data["scenes"]
            else:
                raise ValueError("响应中未找到scenes字段")
                
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试手动解析
            return self._manual_parse_script(content)
    
    def _manual_parse_script(self, content: str) -> List[Dict[str, Any]]:
        """
        手动解析脚本内容（备用方案）
        
        Args:
            content: 待解析的文本内容
            
        Returns:
            解析后的分镜列表
        """
        scenes = []
        
        # 使用正则表达式匹配分镜
        pattern = r'【分镜(\d+)】.*?【旁白】：(.*?)【画面】：(.*?)(?=【分镜|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            scene_number, narration, visual_description = match
            scenes.append({
                "scene_number": int(scene_number),
                "narration": narration.strip(),
                "visual_description": visual_description.strip()
            })
        
        if not scenes:
            # 如果仍然无法解析，创建单个场景
            scenes = [{
                "scene_number": 1,
                "narration": "无法解析的内容，请检查API响应格式。",
                "visual_description": "黑色背景，中央显示错误信息文字。"
            }]
        
        return scenes
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_id,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test."
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception:
            return False 