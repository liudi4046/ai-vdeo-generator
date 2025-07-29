# 🎬 AI视频生成器

一个强大的CLI工具，能够将英文文本转换为引人入胜的中文视频。使用火山引擎的API服务，包括对话生成、语音合成和图像生成功能。

## ✨ 功能特性

- 🤖 **智能脚本生成**: 使用对话API将英文文本转换为结构化的中文视频脚本
- 🎵 **语音合成**: 将中文旁白转换为自然的语音
- 🖼️ **图像生成**: 根据场景描述自动生成配套图像
- 🎞️ **视频合成**: 自动将音频和图像合成为完整视频
- 📱 **用户友好**: 简洁的命令行界面，支持多种参数配置
- 🔧 **高度可配置**: 支持多种语音类型和视频风格

## 🛠️ 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-video-generator
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 系统依赖

确保系统已安装以下软件：

- **FFmpeg**: 用于视频处理
  ```bash
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # macOS
  brew install ffmpeg
  
  # Windows
  # 下载并安装 https://ffmpeg.org/download.html
  ```

## 🔑 配置

### 获取火山引擎API密钥

即使使用免费的文生图服务（500次免费额度），也需要获取火山引擎的访问密钥：

#### Step 1: 注册火山引擎账号
1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 注册或登录账号

#### Step 2: 开通视觉智能服务
1. 在控制台中搜索"视觉智能"
2. 点击进入视觉智能服务
3. 开通智能绘图服务（有500次免费体验额度）

#### Step 3: 获取访问密钥
1. 访问 [访问密钥管理页面](https://console.volcengine.com/iam/keymanage/)
2. 点击"新建访问密钥"
3. 创建并复制 `AccessKey` 和 `SecretKey`
4. **重要**: 妥善保存这些密钥，只会显示一次

#### Step 4: 获取对话API密钥
1. 如果使用的是kimi模型，需要获取ARK_API_KEY
2. 您已经在config.py中提供了密钥: `a295111b-1d1f-49f7-94c1-f8ffb704e090`

### 环境变量设置

```bash
# 对话API密钥（已在config.py中配置，也可通过环境变量覆盖）
export ARK_API_KEY="a295111b-1d1f-49f7-94c1-f8ffb704e090"

# 火山引擎访问密钥和秘密密钥（文生图API，必须设置）
export VOLC_ACCESS_KEY="your_volc_access_key"
export VOLC_SECRET_KEY="your_volc_secret_key"
```

### 免费额度说明

**文生图服务免费额度:**
- 📊 **体验额度**: 500次调用
- 🔄 **并发限制**: 1个
- 💰 **费用**: 完全免费
- ⏰ **有效期**: 通常为1年

**超出免费额度后:**
- 💵 **按次计费**: 0.2元/次
- 📦 **次数包**: 10万次18,000元，50万次80,000元
- 🚀 **并发提升**: 默认2个，可增购

### API配置信息

项目已预配置了语音合成API的信息（无需额外申请）：
- APP ID: `8382474478`
- Access Token: `h3hA0GIgoegUHHNp3_1iR2zYPiljmZMe`
- Voice Type: `zh_female_cancan_mars_bigtts`

## 🚀 快速开始

### 1. 测试API连接

```bash
python main.py test
```

### 2. 从文本生成视频

```bash
# 直接输入文本
python main.py generate "Artificial intelligence is revolutionizing the world..."

# 从文件读取
python main.py from-file input.txt

# 指定输出文件名和语音类型
python main.py generate "Your text here" -o my_video.mp4 -v female
```

### 3. 仅生成脚本

```bash
python main.py script-only "Your English text here" -o script.json
```

## 📝 命令详解

### `generate` - 生成视频

```bash
python main.py generate [OPTIONS] INPUT_TEXT
```

**参数：**
- `INPUT_TEXT`: 英文文本内容或文件路径
- `-o, --output`: 输出视频文件名
- `-v, --voice`: 语音类型 (`female`, `male`, `cancan`, `xinyi`)
- `-s, --style`: 视频风格 (`tech`, `documentary`, `epic`, `casual`)
- `--save-script`: 保存生成的脚本文件
- `--cleanup/--no-cleanup`: 是否清理临时文件

**示例：**
```bash
# 基础用法
python main.py generate "The future of AI is bright"

# 完整配置
python main.py generate "AI technology" -o ai_video.mp4 -v cancan -s tech --save-script
```

### `from-file` - 从文件生成

```bash
python main.py from-file [OPTIONS] TEXT_FILE
```

**示例：**
```bash
python main.py from-file article.txt -o output.mp4 -v female
```

### `test` - 测试API

```bash
python main.py test
```

### `script-only` - 仅生成脚本

```bash
python main.py script-only [OPTIONS] ENGLISH_TEXT
```

### `info` - 显示系统信息

```bash
python main.py info
```

## 🎵 语音类型

| 类型 | 描述 | 声音特点 |
|------|------|----------|
| `cancan` | 罐罐（默认） | 清甜女声 |
| `female` | 通用女声 | 标准女声 |
| `male` | 通用男声 | 标准男声 |
| `xinyi` | 心怡 | 温柔女声 |

## 🎨 视频风格

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| `tech` | 科技感（默认） | 技术文章、产品介绍 |
| `documentary` | 纪录片 | 教育内容、历史故事 |
| `epic` | 史诗感 | 励志内容、宏大主题 |
| `casual` | 轻松休闲 | 日常分享、轻松话题 |

## 📁 输出结构

```
ai-video-generator/
├── output/              # 输出文件目录
│   ├── video_*.mp4     # 生成的视频文件
│   └── script_*.json   # 保存的脚本文件
├── temp/               # 临时文件目录（可自动清理）
│   ├── scene_*_audio.wav  # 临时音频文件
│   └── scene_*_image.jpg  # 临时图像文件
```

## 🐛 常见问题

### Q: API连接失败
A: 检查环境变量是否正确设置，确保网络连接正常。

### Q: 文生图API报错 "access denied"
A: 
1. 确保已获取火山引擎的AK/SK密钥
2. 确保已开通视觉智能服务
3. 检查密钥是否正确设置在环境变量中

### Q: 视频生成失败
A: 确保FFmpeg已正确安装，检查磁盘空间是否充足。

### Q: 语音合成失败
A: 检查语音合成API配置，确保文本内容不为空。

### Q: 免费额度用完了怎么办？
A: 
1. 可以购买次数包或按次付费
2. 或者等待下一个周期的免费额度重置

## 🔧 高级配置

### 自定义配置

编辑 `config.py` 文件可以自定义：
- API端点URL
- 视频参数（分辨率、帧率等）
- 目录路径
- 提示词模板

### 批量处理

创建包含多个文本的文件，使用脚本批量处理：

```bash
# 创建文本列表文件
echo "Text 1" > texts.txt
echo "Text 2" >> texts.txt

# 批量处理
while read line; do
    python main.py generate "$line" -o "video_$(date +%s).mp4"
done < texts.txt
```

## 📊 性能说明

- **脚本生成**: 通常需要10-30秒
- **语音合成**: 每分钟音频约需5-10秒
- **图像生成**: 每张图像约需30-60秒（取决于网络和服务器负载）
- **视频合成**: 根据场景数量，通常需要30秒-2分钟

## 💰 成本估算

**使用免费额度（500次文生图）:**
- 可生成约 50-100 个视频（每个视频5-10个场景）
- 其他服务（语音合成、对话生成）暂无额度限制

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [火山引擎](https://www.volcengine.com/) - 提供强大的AI API服务
- [MoviePy](https://github.com/Zulko/moviepy) - 视频处理库
- [Click](https://click.palletsprojects.com/) - 命令行界面框架 