#!/usr/bin/env python3
"""
CLI演示脚本 - 展示BaseAgent CLI的实际使用
"""

import subprocess
import sys
import time
import json


def run_command(cmd, input_text=None):
    """运行CLI命令"""
    print(f"\n{'='*60}")
    print(f"运行命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            capture_output=True,
            shell=True,
            timeout=30
        )
        
        print("输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
            
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("命令超时")
        return False
    except Exception as e:
        print(f"执行错误: {e}")
        return False


def main():
    """主演示流程"""
    print("=== BaseAgent CLI 演示 ===\n")
    
    # 激活虚拟环境并设置命令前缀
    venv_python = "source venv/bin/activate && python cli.py"
    
    # 1. 显示帮助
    run_command(f"{venv_python} --help")
    time.sleep(1)
    
    # 2. 显示示例
    run_command(f"{venv_python} examples")
    time.sleep(1)
    
    # 3. 显示agent信息
    run_command(f"{venv_python} info")
    time.sleep(1)
    
    # 4. 列出技能
    run_command(f"{venv_python} list-skills")
    time.sleep(1)
    
    # 5. 生成示例配置
    run_command(f"{venv_python} generate-config --output demo-config.json")
    time.sleep(1)
    
    # 6. 显示生成的配置
    print(f"\n{'='*60}")
    print("生成的配置文件内容:")
    print(f"{'='*60}")
    try:
        with open('demo-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(json.dumps(config, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"读取配置文件失败: {e}")
    
    # 7. 手动添加MCP服务器
    print(f"\n{'='*60}")
    print("演示：手动添加MCP服务器")
    print(f"{'='*60}")
    
    # 创建一个简单的MCP服务器脚本
    simple_server = '''#!/usr/bin/env python3
import json
import sys

# 模拟MCP服务器响应
while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
        
        request = json.loads(line.strip())
        request_id = request.get("id")
        method = request.get("method")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "demo-server", "version": "1.0.0"}
                }
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "hello",
                            "description": "Say hello",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Name to greet"}
                                }
                            }
                        }
                    ]
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method {method} not found"}
            }
        
        print(json.dumps(response))
        sys.stdout.flush()
        
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": str(e)}
        }
        print(json.dumps(error_response))
        sys.stdout.flush()
'''
    
    with open('demo_server.py', 'w') as f:
        f.write(simple_server)
    
    # 添加MCP服务器
    run_command(f"{venv_python} add-mcp-server demo-server python demo_server.py")
    time.sleep(1)
    
    # 8. 创建技能文件示例
    skill_instructions = """# 计算器技能

你是一个计算器助手，能够执行各种数学计算。

## 能力
- 基本算术运算（加减乘除）
- 复杂数学计算
- 显示计算步骤
- 处理边界情况

## 使用指南
- 对于复杂问题显示计算步骤
- 使用合适的精度
- 检查边界情况（如除零）
- 使用标准数学符号

## 示例
- "15% of 80" → "0.15 × 80 = 12"
- "Calculate 2^10" → "2^10 = 1024"
- "Square root of 144" → "√144 = 12"
"""
    
    with open('calculator_instructions.md', 'w', encoding='utf-8') as f:
        f.write(skill_instructions)
    
    # 添加技能
    run_command(f"{venv_python} add-skill calculator 'Perform mathematical calculations' calculator_instructions.md --tags math calculator")
    time.sleep(1)
    
    # 9. 最终状态检查
    run_command(f"{venv_python} info")
    time.sleep(1)
    
    print(f"\n{'='*60}")
    print("演示完成！")
    print(f"{'='*60}")
    print("\n要开始对话，请运行:")
    print(f"  {venv_python} chat")
    print("\n或者查看更多命令:")
    print(f"  {venv_python} --help")


if __name__ == "__main__":
    main()