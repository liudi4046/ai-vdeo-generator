import os
import json
from typing import List, Dict, Any
from tqdm import tqdm
from api import ChatAPI, TTSAPI, ImageAPI
from utils import VideoComposer
from config import VIDEO_CONFIG


class VideoGenerator:
    """AI视频生成器主类"""
    
    def __init__(self, chat_api_key: str = None, image_access_key: str = None, 
                 image_secret_key: str = None, temp_dir: str = None, output_dir: str = None):
        """
        初始化视频生成器
        
        Args:
            chat_api_key: 对话API密钥
            image_access_key: 图像API访问密钥
            image_secret_key: 图像API秘密密钥
            temp_dir: 临时文件目录
            output_dir: 输出目录
        """
        # 初始化API客户端
        self.chat_api = ChatAPI(chat_api_key)
        self.tts_api = TTSAPI()
        self.image_api = ImageAPI(image_access_key, image_secret_key)
        
        # 初始化视频合成器
        self.video_composer = VideoComposer(temp_dir, output_dir)
        
        # 设置工作目录
        self.temp_dir = temp_dir or VIDEO_CONFIG["temp_dir"]
        self.output_dir = output_dir or VIDEO_CONFIG["output_dir"]
        
        # 确保目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 统计信息
        self.stats = {
            "scenes_generated": 0,
            "images_generated": 0,
            "audio_generated": 0,
            "total_duration": 0.0
        }
    
    def generate_video_from_text(self, english_text: str, output_filename: str = None,
                                voice_type: str = None, video_style: str = "standard") -> str:
        """
        从英文文本生成完整视频
        
        Args:
            english_text: 输入的英文文本
            output_filename: 输出视频文件名
            voice_type: 语音类型
            video_style: 视频风格
            
        Returns:
            输出视频文件路径
        """
        print("🎬 开始AI视频生成流程...")
        print(f"📝 输入文本长度: {len(english_text)} 字符")
        
        try:
            # 第一步：生成视频脚本
            print("\n📋 第1步：生成视频脚本...")
            scenes = self._generate_script(english_text)
            self.stats["scenes_generated"] = len(scenes)
            print(f"✅ 成功生成 {len(scenes)} 个分镜")
            
            # 第二步：生成音频和图像
            print("\n🎵 第2步：生成音频和图像...")
            scenes_data = self._generate_media_files(scenes, voice_type)
            
            # 第三步：合成视频
            print("\n🎞️ 第3步：合成视频...")
            video_path = self._compose_video(scenes_data, output_filename)
            
            print(f"\n🎉 视频生成完成！")
            print(f"📁 输出路径: {video_path}")
            print(f"📊 统计信息:")
            print(f"   - 分镜数量: {self.stats['scenes_generated']}")
            print(f"   - 生成图像: {self.stats['images_generated']}")
            print(f"   - 生成音频: {self.stats['audio_generated']}")
            print(f"   - 总时长: {self.stats['total_duration']:.1f}秒")
            
            return video_path
            
        except Exception as e:
            print(f"❌ 视频生成失败: {e}")
            raise
    
    def _generate_script(self, english_text: str) -> List[Dict[str, Any]]:
        """生成视频脚本"""
        try:
            scenes = self.chat_api.generate_script(english_text)
            
            # 验证脚本格式
            for i, scene in enumerate(scenes):
                if not isinstance(scene, dict):
                    raise ValueError(f"场景 {i+1} 格式错误")
                
                required_fields = ["scene_number", "narration", "visual_description"]
                for field in required_fields:
                    if field not in scene:
                        raise ValueError(f"场景 {i+1} 缺少必要字段: {field}")
            
            return scenes
            
        except Exception as e:
            raise Exception(f"脚本生成失败: {e}")
    
    def _generate_media_files(self, scenes: List[Dict[str, Any]], voice_type: str = None) -> List[Dict[str, Any]]:
        """生成媒体文件（音频和图像）"""
        scenes_data = []
        
        for i, scene in enumerate(tqdm(scenes, desc="生成媒体文件")):
            scene_data = {
                "scene_number": scene["scene_number"],
                "narration": scene["narration"],
                "visual_description": scene["visual_description"]
            }
            
            # 生成音频文件
            audio_filename = f"scene_{i+1:03d}_audio.wav"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            
            print(f"\n🎵 生成第 {i+1} 个场景的音频...")
            if self.tts_api.text_to_speech(scene["narration"], audio_path, voice_type):
                scene_data["audio_path"] = audio_path
                scene_data["duration"] = self.video_composer.get_audio_duration(audio_path)
                self.stats["audio_generated"] += 1
                self.stats["total_duration"] += scene_data["duration"]
                print(f"✅ 音频生成成功 (时长: {scene_data['duration']:.1f}秒)")
            else:
                # 如果音频生成失败，使用估算时长
                scene_data["audio_path"] = ""
                scene_data["duration"] = self.tts_api.estimate_duration(scene["narration"])
                print(f"⚠️ 音频生成失败，使用估算时长: {scene_data['duration']:.1f}秒")
            
            # 生成图像文件
            image_filename = f"scene_{i+1:03d}_image.jpg"
            image_path = os.path.join(self.temp_dir, image_filename)
            
            print(f"🖼️ 生成第 {i+1} 个场景的图像...")
            if self.image_api.generate_image(scene["visual_description"], image_path):
                scene_data["image_path"] = image_path
                self.stats["images_generated"] += 1
                print(f"✅ 图像生成成功")
            else:
                # 如果图像生成失败，创建一个简单的占位图像
                scene_data["image_path"] = self._create_placeholder_image(image_path, scene["visual_description"])
                print(f"⚠️ 图像生成失败，使用占位图像")
            
            scenes_data.append(scene_data)
        
        return scenes_data
    
    def _create_placeholder_image(self, output_path: str, description: str) -> str:
        """创建占位图像"""
        try:
            import cv2
            import numpy as np
            
            # 创建黑色背景
            img = np.zeros((VIDEO_CONFIG["height"], VIDEO_CONFIG["width"], 3), dtype=np.uint8)
            
            # 添加文字
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = "图像生成失败"
            text_size = cv2.getTextSize(text, font, 1, 2)[0]
            text_x = (img.shape[1] - text_size[0]) // 2
            text_y = (img.shape[0] + text_size[1]) // 2
            
            cv2.putText(img, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
            
            # 保存图像
            cv2.imwrite(output_path, img)
            return output_path
            
        except Exception:
            # 如果OpenCV不可用，创建一个简单的文本文件作为标记
            with open(output_path + ".txt", "w", encoding="utf-8") as f:
                f.write(f"占位图像：{description}")
            return output_path + ".txt"
    
    def _compose_video(self, scenes_data: List[Dict[str, Any]], output_filename: str = None) -> str:
        """合成视频"""
        if not scenes_data:
            raise ValueError("没有场景数据可以合成视频")
        
        try:
            return self.video_composer.create_video_from_scenes(scenes_data, output_filename)
        except Exception as e:
            raise Exception(f"视频合成失败: {e}")
    
    def test_apis(self) -> Dict[str, bool]:
        """测试所有API连接"""
        print("🧪 测试API连接...")
        
        results = {}
        
        # 测试对话API
        print("  - 测试对话API...", end=" ")
        try:
            results["chat_api"] = self.chat_api.test_connection()
            print("✅" if results["chat_api"] else "❌")
        except Exception as e:
            results["chat_api"] = False
            print(f"❌ ({e})")
        
        # 测试语音合成API
        print("  - 测试语音合成API...", end=" ")
        try:
            results["tts_api"] = self.tts_api.test_connection()
            print("✅" if results["tts_api"] else "❌")
        except Exception as e:
            results["tts_api"] = False
            print(f"❌ ({e})")
        
        # 测试图像生成API
        print("  - 测试图像生成API...", end=" ")
        try:
            results["image_api"] = self.image_api.test_connection()
            print("✅" if results["image_api"] else "❌")
        except Exception as e:
            results["image_api"] = False
            print(f"❌ ({e})")
        
        all_passed = all(results.values())
        print(f"\n📊 API测试结果: {'全部通过' if all_passed else '部分失败'}")
        
        return results
    
    def save_script_to_file(self, scenes: List[Dict[str, Any]], filename: str = None) -> str:
        """保存脚本到文件"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"script_{timestamp}.json"
        
        script_path = os.path.join(self.output_dir, filename)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)
        
        return script_path
    
    def load_script_from_file(self, script_path: str) -> List[Dict[str, Any]]:
        """从文件加载脚本"""
        with open(script_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def cleanup(self):
        """清理临时文件"""
        self.video_composer.cleanup_temp_files()
        print("🧹 清理临时文件完成") 