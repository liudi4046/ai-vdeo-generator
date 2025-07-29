import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
from pydub import AudioSegment
from pydub.utils import which
from typing import List, Tuple
from config import VIDEO_CONFIG


class VideoComposer:
    """视频合成器"""
    
    def __init__(self, temp_dir: str = None, output_dir: str = None):
        """
        初始化视频合成器
        
        Args:
            temp_dir: 临时文件目录
            output_dir: 输出目录
        """
        self.temp_dir = temp_dir or VIDEO_CONFIG["temp_dir"]
        self.output_dir = output_dir or VIDEO_CONFIG["output_dir"]
        self.fps = VIDEO_CONFIG["fps"]
        self.video_format = VIDEO_CONFIG["output_format"]
        
        # 确保目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 检查ffmpeg是否可用
        if not which("ffmpeg"):
            print("警告: 未找到ffmpeg，某些功能可能不可用")
    
    def create_video_from_scenes(self, scenes_data: List[dict], output_filename: str = None) -> str:
        """
        从场景数据创建视频
        
        Args:
            scenes_data: 场景数据列表，每个元素包含:
                - audio_path: 音频文件路径
                - image_path: 图像文件路径
                - duration: 持续时间（秒）
            output_filename: 输出文件名
            
        Returns:
            输出视频文件路径
        """
        if not scenes_data:
            raise ValueError("场景数据不能为空")
        
        # 生成输出文件名
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"video_{timestamp}.{self.video_format}"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 创建视频片段列表
            video_clips = []
            
            for i, scene in enumerate(scenes_data):
                print(f"处理场景 {i+1}/{len(scenes_data)}...")
                
                # 创建图像视频片段
                if os.path.exists(scene['image_path']):
                    image_clip = ImageClip(scene['image_path'])
                    image_clip = image_clip.set_duration(scene['duration'])
                    
                    # 如果有音频文件，设置音频
                    if os.path.exists(scene['audio_path']):
                        audio_clip = AudioFileClip(scene['audio_path'])
                        image_clip = image_clip.set_audio(audio_clip)
                    
                    video_clips.append(image_clip)
                else:
                    print(f"警告: 图像文件不存在: {scene['image_path']}")
            
            if not video_clips:
                raise ValueError("没有有效的视频片段")
            
            # 合并所有视频片段
            print("合并视频片段...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # 输出视频
            print(f"输出视频到: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile_path=os.path.join(self.temp_dir, 'temp_audio.wav'),
                remove_temp=True
            )
            
            # 清理资源
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"视频合成失败: {e}")
            raise
    
    def create_simple_video(self, audio_paths: List[str], image_paths: List[str], 
                           durations: List[float], output_filename: str = None) -> str:
        """
        创建简单视频（每个场景一个图像和音频）
        
        Args:
            audio_paths: 音频文件路径列表
            image_paths: 图像文件路径列表
            durations: 每个场景的持续时间列表
            output_filename: 输出文件名
            
        Returns:
            输出视频文件路径
        """
        if len(audio_paths) != len(image_paths) or len(audio_paths) != len(durations):
            raise ValueError("音频、图像和持续时间列表长度必须相同")
        
        scenes_data = []
        for audio_path, image_path, duration in zip(audio_paths, image_paths, durations):
            scenes_data.append({
                'audio_path': audio_path,
                'image_path': image_path,
                'duration': duration
            })
        
        return self.create_video_from_scenes(scenes_data, output_filename)
    
    def add_background_music(self, video_path: str, music_path: str, 
                           music_volume: float = 0.3, output_filename: str = None) -> str:
        """
        为视频添加背景音乐
        
        Args:
            video_path: 视频文件路径
            music_path: 背景音乐文件路径
            music_volume: 背景音乐音量（0.0-1.0）
            output_filename: 输出文件名
            
        Returns:
            输出视频文件路径
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"音乐文件不存在: {music_path}")
        
        # 生成输出文件名
        if not output_filename:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_filename = f"{base_name}_with_music.{self.video_format}"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 加载视频和音乐
            video = VideoFileClip(video_path)
            music = AudioFileClip(music_path)
            
            # 调整音乐长度和音量
            music = music.subclip(0, video.duration)
            music = music.volumex(music_volume)
            
            # 混合音频
            if video.audio:
                final_audio = CompositeAudioClip([video.audio, music])
            else:
                final_audio = music
            
            # 设置新音频
            final_video = video.set_audio(final_audio)
            
            # 输出视频
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 清理资源
            video.close()
            music.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"添加背景音乐失败: {e}")
            raise
    
    def create_slideshow_video(self, image_paths: List[str], audio_path: str = None,
                             duration_per_image: float = 3.0, transition_duration: float = 0.5,
                             output_filename: str = None) -> str:
        """
        创建幻灯片式视频
        
        Args:
            image_paths: 图像文件路径列表
            audio_path: 音频文件路径（可选）
            duration_per_image: 每张图片的显示时间
            transition_duration: 转场时间
            output_filename: 输出文件名
            
        Returns:
            输出视频文件路径
        """
        if not image_paths:
            raise ValueError("图像路径列表不能为空")
        
        # 生成输出文件名
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"slideshow_{timestamp}.{self.video_format}"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 创建图像片段
            clips = []
            for i, image_path in enumerate(image_paths):
                if os.path.exists(image_path):
                    clip = ImageClip(image_path)
                    clip = clip.set_duration(duration_per_image)
                    
                    # 添加淡入淡出效果
                    if transition_duration > 0:
                        clip = clip.fadein(transition_duration).fadeout(transition_duration)
                    
                    clips.append(clip)
                else:
                    print(f"警告: 图像文件不存在: {image_path}")
            
            if not clips:
                raise ValueError("没有有效的图像文件")
            
            # 合并片段
            video = concatenate_videoclips(clips, method="compose")
            
            # 添加音频（如果提供）
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                # 调整音频长度
                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                elif audio.duration < video.duration:
                    # 循环播放音频
                    loops = int(video.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops)
                    audio = audio.subclip(0, video.duration)
                
                video = video.set_audio(audio)
            
            # 输出视频
            video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac' if video.audio else None
            )
            
            # 清理资源
            video.close()
            for clip in clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"创建幻灯片视频失败: {e}")
            raise
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频文件的持续时间
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            持续时间（秒）
        """
        try:
            if os.path.exists(audio_path):
                audio = AudioSegment.from_file(audio_path)
                return len(audio) / 1000.0  # 转换为秒
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            print(f"清理临时文件失败: {e}")


# 补充导入moviepy的concatenate_videoclips
try:
    from moviepy.editor import concatenate_videoclips, CompositeAudioClip, concatenate_audioclips
except ImportError:
    print("警告: moviepy导入失败，请确保已正确安装")
    # 提供备用函数
    def concatenate_videoclips(clips, method="compose"):
        raise NotImplementedError("moviepy未正确安装")
    
    def CompositeAudioClip(clips):
        raise NotImplementedError("moviepy未正确安装")
    
    def concatenate_audioclips(clips):
        raise NotImplementedError("moviepy未正确安装") 