#!/usr/bin/env python3
"""
快速开始脚本 - 演示BaseAgent CLI的基本用法
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd):
    """运行命令并显示结果"""
    print(f"\n>>> {cmd}")
    print("-" * 60)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except subprocess.TimeoutExpired:
        print("命令超时")
    except Exception as e:
        print(f"执行错误: {e}")


def main():
    """演示CLI基本用法"""
    print("=== BaseAgent CLI 快速开始 ===\n")
    
    # 确保在虚拟环境中
    venv_path = Path("venv/bin/activate")
    if not venv_path.exists():
        print("请先创建虚拟环境: python3 -m venv venv && source venv/bin/activate")
        return
    
    # 演示基本命令
    commands = [
        "python cli.py --help",
        "python cli.py examples", 
        "python cli.py info",
        "python cli.py list-skills",
        "python cli.py generate-config --output quick-start-config.json",
        "python cli.py load-mcp-config sample-mcp-config.json",
        "python cli.py list-mcp"
    ]
    
    for cmd in commands:
        run_command(cmd)
    
    print(f"\n{'='*60}")
    print("快速开始完成！")
    print(f"{'='*60}")
    print("\n要开始对话（需要API密钥）:")
    print("export OPENAI_API_KEY=your-api-key")
    print("python cli.py chat")
    print("\n或者查看完整文档:")
    print("cat CLI_README.md")


if __name__ == "__main__":
    main()