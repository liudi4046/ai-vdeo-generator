#!/usr/bin/env python3
"""
AI视频生成器 - 英文转中文视频的CLI工具

使用火山引擎API将英文文本转换为中文旁白视频
"""

import os
import sys
import click
from pathlib import Path
from colorama import init, Fore, Style
from video_generator import VideoGenerator

# 初始化colorama（Windows兼容性）
init()

def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                     🎬 AI视频生成器 🎬                        ║
║                                                              ║
║              将英文文本转换为引人入胜的中文视频                   ║
║                     基于火山引擎API                           ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def validate_file_path(ctx, param, value):
    """验证文件路径"""
    if value and not os.path.exists(value):
        raise click.BadParameter(f'文件不存在: {value}')
    return value

def validate_api_keys():
    """验证API密钥配置"""
    required_env_vars = {
        'ARK_API_KEY': '对话API密钥',
        'VOLC_ACCESS_KEY': '火山引擎访问密钥',
        'VOLC_SECRET_KEY': '火山引擎秘密密钥'
    }
    
    missing_vars = []
    for var, desc in required_env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  {var} ({desc})")
    
    if missing_vars:
        print(f"{Fore.RED}❌ 缺少必要的环境变量:{Style.RESET_ALL}")
        for var in missing_vars:
            print(var)
        print(f"\n{Fore.YELLOW}请设置环境变量后重试，例如:{Style.RESET_ALL}")
        print("export ARK_API_KEY='your_ark_api_key'")
        print("export VOLC_ACCESS_KEY='your_volc_access_key'")
        print("export VOLC_SECRET_KEY='your_volc_secret_key'")
        return False
    
    return True

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """AI视频生成器 - 将英文文本转换为中文视频"""
    print_banner()

@cli.command()
@click.argument('input_text')
@click.option('--output', '-o', help='输出视频文件名')
@click.option('--voice', '-v', 
              type=click.Choice(['female', 'male', 'cancan', 'xinyi']), 
              default='cancan',
              help='语音类型 (默认: cancan)')
@click.option('--style', '-s',
              type=click.Choice(['tech', 'documentary', 'epic', 'casual']),
              default='tech',
              help='视频风格 (默认: tech)')
@click.option('--save-script', is_flag=True, help='保存生成的脚本文件')
@click.option('--cleanup/--no-cleanup', default=True, help='是否清理临时文件')
def generate(input_text, output, voice, style, save_script, cleanup):
    """从英文文本生成视频
    
    INPUT_TEXT: 英文文本内容（直接输入或文件路径）
    """
    # 验证API密钥
    if not validate_api_keys():
        sys.exit(1)
    
    # 处理输入文本
    if os.path.exists(input_text):
        print(f"📖 从文件读取文本: {input_text}")
        with open(input_text, 'r', encoding='utf-8') as f:
            english_text = f.read().strip()
    else:
        english_text = input_text
    
    if not english_text:
        print(f"{Fore.RED}❌ 输入文本为空{Style.RESET_ALL}")
        sys.exit(1)
    
    # 语音类型映射
    voice_mapping = {
        'female': 'zh_female_cancan_mars_bigtts',
        'male': 'zh_male_M392_conversation_wvae_bigtts',
        'cancan': 'zh_female_cancan_mars_bigtts',
        'xinyi': 'zh_female_xinyi_mars_bigtts'
    }
    
    try:
        # 初始化视频生成器
        generator = VideoGenerator(
            chat_api_key=os.getenv('ARK_API_KEY'),
            image_access_key=os.getenv('VOLC_ACCESS_KEY'),
            image_secret_key=os.getenv('VOLC_SECRET_KEY')
        )
        
        # 生成视频
        video_path = generator.generate_video_from_text(
            english_text=english_text,
            output_filename=output,
            voice_type=voice_mapping.get(voice),
            video_style=style
        )
        
        # 保存脚本（如果需要）
        if save_script:
            script_path = generator.save_script_to_file(
                generator._generate_script(english_text)
            )
            print(f"📄 脚本已保存到: {script_path}")
        
        # 清理临时文件
        if cleanup:
            generator.cleanup()
        
        print(f"\n{Fore.GREEN}🎉 视频生成成功！{Style.RESET_ALL}")
        print(f"📁 输出文件: {video_path}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 生成失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('text_file', callback=validate_file_path)
@click.option('--output', '-o', help='输出视频文件名')
@click.option('--voice', '-v', 
              type=click.Choice(['female', 'male', 'cancan', 'xinyi']), 
              default='cancan',
              help='语音类型')
def from_file(text_file, output, voice):
    """从文件生成视频
    
    TEXT_FILE: 包含英文文本的文件路径
    """
    # 验证API密钥
    if not validate_api_keys():
        sys.exit(1)
    
    try:
        # 读取文件内容
        with open(text_file, 'r', encoding='utf-8') as f:
            english_text = f.read().strip()
        
        if not english_text:
            print(f"{Fore.RED}❌ 文件内容为空{Style.RESET_ALL}")
            sys.exit(1)
        
        # 调用生成函数
        ctx = click.get_current_context()
        ctx.invoke(generate, 
                  input_text=english_text, 
                  output=output,
                  voice=voice,
                  style='tech',
                  save_script=False,
                  cleanup=True)
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 读取文件失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
def test():
    """测试API连接"""
    print("🧪 测试API连接状态...\n")
    
    # 验证API密钥
    if not validate_api_keys():
        sys.exit(1)
    
    try:
        generator = VideoGenerator(
            chat_api_key=os.getenv('ARK_API_KEY'),
            image_access_key=os.getenv('VOLC_ACCESS_KEY'),
            image_secret_key=os.getenv('VOLC_SECRET_KEY')
        )
        
        results = generator.test_apis()
        
        print("\n" + "="*50)
        all_passed = all(results.values())
        
        if all_passed:
            print(f"{Fore.GREEN}✅ 所有API连接正常！{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ 部分API连接失败，请检查配置{Style.RESET_ALL}")
            failed_apis = [api for api, status in results.items() if not status]
            print(f"失败的API: {', '.join(failed_apis)}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 测试失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
@click.argument('english_text')
@click.option('--output', '-o', default='script.json', help='输出脚本文件名')
def script_only(english_text, output):
    """仅生成视频脚本（不生成视频）
    
    ENGLISH_TEXT: 英文文本内容
    """
    # 验证API密钥
    if not validate_api_keys():
        sys.exit(1)
    
    try:
        generator = VideoGenerator(
            chat_api_key=os.getenv('ARK_API_KEY'),
            image_access_key=os.getenv('VOLC_ACCESS_KEY'),
            image_secret_key=os.getenv('VOLC_SECRET_KEY')
        )
        
        print("📋 生成视频脚本...")
        scenes = generator._generate_script(english_text)
        
        script_path = generator.save_script_to_file(scenes, output)
        
        print(f"\n{Fore.GREEN}✅ 脚本生成成功！{Style.RESET_ALL}")
        print(f"📄 脚本文件: {script_path}")
        print(f"📊 分镜数量: {len(scenes)}")
        
        # 显示脚本预览
        print(f"\n{Fore.CYAN}脚本预览:{Style.RESET_ALL}")
        for i, scene in enumerate(scenes[:3]):  # 显示前3个场景
            print(f"  场景 {scene['scene_number']}: {scene['narration'][:50]}...")
        
        if len(scenes) > 3:
            print(f"  ... 还有 {len(scenes) - 3} 个场景")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ 脚本生成失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

@cli.command()
def info():
    """显示系统信息和配置"""
    print("📋 系统信息:")
    print(f"  Python版本: {sys.version}")
    print(f"  工作目录: {os.getcwd()}")
    
    print(f"\n🔧 环境变量检查:")
    env_vars = ['ARK_API_KEY', 'VOLC_ACCESS_KEY', 'VOLC_SECRET_KEY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 只显示前几个字符，保护敏感信息
            masked_value = value[:8] + '*' * (len(value) - 8) if len(value) > 8 else '*' * len(value)
            print(f"  {var}: {masked_value}")
        else:
            print(f"  {var}: {Fore.RED}未设置{Style.RESET_ALL}")
    
    print(f"\n📁 输出目录:")
    print(f"  临时文件: ./temp")
    print(f"  输出文件: ./output")

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ 用户中断操作{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ 未预期的错误: {e}{Style.RESET_ALL}")
        sys.exit(1) 