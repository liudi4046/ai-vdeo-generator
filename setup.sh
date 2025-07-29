#!/bin/bash

# AI视频生成器 - 快速设置脚本

echo "🎬 AI视频生成器 - 快速设置"
echo "================================"

# 检查Python版本
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python 3.8+"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $python_version"

# 检查FFmpeg
echo "📋 检查FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ FFmpeg 未找到"
    echo "请安装FFmpeg以支持视频生成功能:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: 从 https://ffmpeg.org/download.html 下载"
else
    echo "✅ FFmpeg 已安装"
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装完成"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 创建必要的目录
echo "📁 创建工作目录..."
mkdir -p temp output
echo "✅ 目录创建完成"

# 提示用户设置环境变量
echo ""
echo "🔑 请设置以下环境变量:"
echo "================================"
echo "export ARK_API_KEY='your_ark_api_key'"
echo "export VOLC_ACCESS_KEY='your_volc_access_key'" 
echo "export VOLC_SECRET_KEY='your_volc_secret_key'"
echo ""
echo "或者将它们添加到 ~/.bashrc 或 ~/.zshrc 文件中"
echo ""

# 测试安装
echo "🧪 测试安装..."
if [[ -n "$ARK_API_KEY" && -n "$VOLC_ACCESS_KEY" && -n "$VOLC_SECRET_KEY" ]]; then
    echo "🚀 运行API连接测试..."
    python3 main.py test
else
    echo "⚠️ 环境变量未设置，跳过API测试"
    echo "设置环境变量后，运行以下命令测试:"
    echo "python3 main.py test"
fi

echo ""
echo "🎉 设置完成！"
echo "尝试生成你的第一个视频:"
echo "python3 main.py generate 'Hello world, this is AI video generation!'"
echo ""
echo "查看更多命令:"
echo "python3 main.py --help" 