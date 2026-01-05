#!/usr/bin/env python3
"""
简化版CLI测试脚本 - 直接在当前Python环境中测试功能
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 添加项目路径到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from cli import cli, get_agent
from click.testing import CliRunner


def test_cli_commands():
    """测试CLI命令"""
    print("=== BaseAgent CLI 测试 ===\n")
    
    runner = CliRunner()
    
    # 测试1: 查看帮助
    print("1. 测试帮助命令...")
    result = runner.invoke(cli, ['--help'])
    if result.exit_code == 0:
        print("✓ 帮助命令成功")
        print(f"输出前几行: {result.output[:200]}...")
    else:
        print("✗ 帮助命令失败")
        print(f"错误: {result.output}")
    print()
    
    # 测试2: 查看示例
    print("2. 测试示例命令...")
    result = runner.invoke(cli, ['examples'])
    if result.exit_code == 0:
        print("✓ 示例命令成功")
        print("示例输出:")
        print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
    else:
        print("✗ 示例命令失败")
        print(f"错误: {result.output}")
    print()
    
    # 测试3: 查看信息
    print("3. 测试信息命令...")
    result = runner.invoke(cli, ['info'])
    if result.exit_code == 0:
        print("✓ 信息命令成功")
        print("信息输出:")
        print(result.output)
    else:
        print("✗ 信息命令失败")
        print(f"错误: {result.output}")
    print()
    
    # 测试4: 列出技能
    print("4. 测试列出技能...")
    result = runner.invoke(cli, ['list-skills'])
    if result.exit_code == 0:
        print("✓ 列出技能成功")
        print("技能列表:")
        print(result.output)
    else:
        print("✗ 列出技能失败")
        print(f"错误: {result.output}")
    print()
    
    # 测试5: 生成配置文件
    print("5. 测试生成配置文件...")
    result = runner.invoke(cli, ['generate-config', '--output', 'test-config.json'])
    if result.exit_code == 0:
        print("✓ 生成配置文件成功")
        print(f"输出: {result.output}")
        
        # 检查文件是否生成
        if Path('test-config.json').exists():
            print("✓ 配置文件已生成")
            with open('test-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("配置文件内容:")
            print(json.dumps(config, indent=2, ensure_ascii=False)[:300] + "...")
        else:
            print("✗ 配置文件未生成")
    else:
        print("✗ 生成配置文件失败")
        print(f"错误: {result.output}")
    print()
    
    # 测试6: 直接在Python中测试agent功能
    print("6. 测试BaseAgent功能...")
    try:
        # 创建agent实例
        agent = get_agent(CliRunner().make_context('cli', []))
        
        # 测试列出技能
        skills = asyncio.run(agent.list_all_skills())
        print(f"✓ 列出技能成功: {len(skills['skills'])} 个技能")
        
        # 测试生成配置
        tools = asyncio.run(agent.list_all_tools())
        print(f"✓ 列出工具成功: {len(tools.get('mcp_tools', {}))} 个MCP服务器")
        
        # 清理
        asyncio.run(agent.close())
        
    except Exception as e:
        print(f"✗ BaseAgent功能测试失败: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 测试7: 模拟加载MCP配置和列出
    print("7. 测试连续命令...")
    with runner.isolated_filesystem():
        # 创建测试配置
        config_data = {
            "mcpServers": {
                "test-server": {
                    "command": ["echo", "test"],
                    "env": {"TEST": "value"}
                }
            }
        }
        
        with open('test-mcp.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # 加载配置
        result1 = runner.invoke(cli, ['load-mcp-config', 'test-mcp.json'])
        print(f"加载配置结果: {result1.output}")
        
        # 列出MCP服务器
        result2 = runner.invoke(cli, ['list-mcp'])
        print(f"列出MCP结果: {result2.output}")
    
    print()
    print("=== 测试完成 ===")


def create_sample_files():
    """创建示例文件"""
    print("创建示例文件...")
    
    # 创建示例技能文件
    skill_content = """# 计算器技能

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
"""
    
    with open('sample_skill.md', 'w', encoding='utf-8') as f:
        f.write(skill_content)
    print("✓ 创建示例技能文件: sample_skill.md")
    
    # 创建示例MCP配置文件
    mcp_config = {
        "mcpServers": {
            "filesystem": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {"TZ": "Asia/Shanghai"}
            },
            "time_service": {
                "command": ["python", "time_service.py"],
                "env": {"TZ": "Asia/Shanghai"}
            }
        }
    }
    
    with open('sample-mcp-config.json', 'w', encoding='utf-8') as f:
        json.dump(mcp_config, f, indent=2, ensure_ascii=False)
    print("✓ 创建示例MCP配置: sample-mcp-config.json")
    
    # 创建简单MCP服务器
    server_content = '''#!/usr/bin/env python3
import json
import sys

def handle_request(request):
    request_id = request.get("id")
    method = request.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "demo", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
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
                                "name": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method {method} not found"}
        }

if __name__ == "__main__":
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except:
            break
'''
    
    with open('demo_server.py', 'w') as f:
        f.write(server_content)
    print("✓ 创建示例MCP服务器: demo_server.py")


def main():
    """主函数"""
    print("BaseAgent CLI 完整测试\n")
    
    # 创建示例文件
    create_sample_files()
    print()
    
    # 运行测试
    test_cli_commands()
    
    print("\n可用文件:")
    print("- sample_skill.md - 示例技能文件")
    print("- sample-mcp-config.json - 示例MCP配置")
    print("- demo_server.py - 示例MCP服务器")
    print("- CLI_README.md - 完整文档")
    print("\n快速开始:")
    print("1. python cli.py examples - 查看使用示例")
    print("2. python cli.py generate-config --output my-config.json - 生成配置")
    print("3. python cli.py load-mcp-config sample-mcp-config.json - 加载配置")
    print("4. python cli.py chat - 开始对话（需要设置OPENAI_API_KEY）")


if __name__ == "__main__":
    main()