# 火山引擎API配置

# 对话API配置
CHAT_API_CONFIG = {
    "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "model_id": "kimi-k2-250711",
    "api_key": "a295111b-1d1f-49f7-94c1-f8ffb704e090",  # 需要在环境变量或运行时设置
}

# 语音合成API配置
TTS_API_CONFIG = {
    "websocket_url": "wss://openspeech.bytedance.com/api/v1/tts/ws_binary",
    "http_url": "https://openspeech.bytedance.com/api/v1/tts",
    "app_id": "8382474478",
    "access_token": "h3hA0GIgoegUHHNp3_1iR2zYPiljmZMe",
    "secret_key": "A1YWgGWqkHKba-QrheeeaiMhIuZXsxHi",
    "voice_type": "zh_female_cancan_mars_bigtts",  # 默认音色
    "cluster": "volcano_tts"
}

# 文生图API配置
# 注意：即使使用免费额度（500次），也需要通过火山引擎访问控制获取AK/SK
# 获取步骤：
# 1. 访问 https://console.volcengine.com/iam/keymanage/
# 2. 点击"新建访问密钥"
# 3. 创建AccessKey和SecretKey
# 4. 确保账号已开通视觉智能服务权限
IMAGE_API_CONFIG = {
    "base_url": "https://visual.volcengineapi.com",
    "req_key": "high_aes_general_v30l_zt2i",
    "region": "cn-north-1",
    "service": "cv",
    "action": "CVProcess",
    "version": "2022-08-31",
    "access_key": "AKLTYTdiOGFkNzEyZGQwNDY3MWI0YTkxN2I1MTlmZDI0YTk",  # 必须设置！从火山引擎访问控制获取
    "secret_key": "Wm1ObVltRXpZamhpWldNeE5EUm1ObUU0TkRZd016STRZVEpqTkRjME5EZw==",  # 必须设置！从火山引擎访问控制获取
    
    # 免费额度说明：
    # - 体验额度：500次调用
    # - 并发限制：1
    # - 费用：免费
    # 
    # 付费状态说明：
    # - 并发限制：2（可增购）
    # - 按调用次数计费：0.2元/次
    # - 次数包：10万次18,000元，50万次80,000元
}

# 视频输出配置
VIDEO_CONFIG = {
    "fps": 24,
    "width": 1328,
    "height": 1328,
    "output_format": "mp4",
    "audio_format": "wav",
    "temp_dir": "./temp",
    "output_dir": "./output"
}

# 生成脚本的Prompt模板
SCRIPT_GENERATION_PROMPT = """# 角色

你是一位顶级的视频编剧和导演，擅长将复杂的英文信息转化为引人入胜的中文视频脚本。你的作品节奏明快、情感饱满、画面感极强。

# 任务

你的任务是将我提供的【英文原文】转换成一个结构化的中文视频脚本，该脚本将用于AI视频生成。请严格遵循以下所有指示。

# 核心指令

1. **风格转换**：请勿进行生硬的直译。你需要用意译和再创作的方式，将原文内容转换成流畅、自然、且极具吸引力的中文口语旁白。想象你是在对观众讲一个精彩的故事。

2. **分镜结构**：将整个故事拆分成多个【分镜】。每个分镜都代表一个独立的视觉场景和一小段旁白。这有助于创造动态的视觉节奏。

3. **格式要求**：每一个【分镜】都必须包含两个部分：
   - **【旁白】**：这是AI需要朗读的中文文本。请使用简短、有力、易于理解的句子。
   - **【画面】**：这是对该场景视觉内容的详细描述。请描绘出具体的影像、镜头运动（如推、拉、摇、移）、氛围、色彩和任何需要的屏幕文字或特效。

4. **节奏控制**：每个【分镜】的旁白长度应适中，大约对应15到45秒的朗读时间。

5. **目标受众**：对前沿科技和创新内容感兴趣的年轻人和普通大众。

6. **视频风格**：整体视频的基调为科技感纪录片风格，富有启发性和现代感。

# 输出格式

请严格按照以下JSON格式输出：

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "narration": "这里是旁白内容",
      "visual_description": "这里是画面描述"
    }
  ]
}
```

# 英文原文

{english_text}

# 开始生成

请根据以上所有要求，生成结构化的视频脚本。""" 