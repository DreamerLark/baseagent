# BaseAgent CLI 文档

## 概述

BaseAgent CLI 是一个命令行工具，提供了 BaseAgent 的完整功能，包括技能（Skills）和 MCP（Model Context Protocol）服务器支持。

## 功能特性

- **交互式对话**: 与 BaseAgent 进行实时对话
- **技能管理**: 注册、列出和管理 Anthropic Skills
- **MCP 服务器管理**: 从配置文件加载和管理 MCP 服务器
- **配置生成**: 生成示例 MCP 配置文件
- **状态查看**: 查看 agent 配置和状态信息

## 安装和设置

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

```bash
# 设置 OpenAI API 密钥（必需）
export OPENAI_API_KEY="your-openai-api-key"

# 设置模型（可选，默认为 gpt-4-turbo-preview）
export OPENAI_MODEL="gpt-4-turbo-preview"

# 设置 API 基础 URL（可选）
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

或者创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件并添加你的 API 密钥
```

## 基本使用

### 查看帮助

```bash
python cli.py --help
```

### 查看使用示例

```bash
python cli.py examples
```

### 查看 Agent 信息

```bash
python cli.py info
```

## 技能管理

### 列出所有技能

```bash
python cli.py list-skills
```

### 添加新技能

```bash
python cli.py add-skill 技能名称 "技能描述" 指令文件.md
```

示例：

```bash
python cli.py add-skill calculator "Perform mathematical calculations" calculator_instructions.md --tags math calculator
```

技能指令文件示例（`calculator_instructions.md`）：

```markdown
# 计算器技能

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
```

## MCP 服务器管理

### 列出 MCP 服务器

```bash
python cli.py list-mcp
```

### 生成示例配置

```bash
python cli.py generate-config --output mcp-config.json
```

### 从配置文件加载 MCP 服务器

```bash
python cli.py load-mcp-config mcp-config.json
```

### 手动添加 MCP 服务器

```bash
python cli.py add-mcp-server 服务器名称 命令 参数
```

示例：

```bash
# 添加文件系统服务器
python cli.py add-mcp-server filesystem npx -y @modelcontextprotocol/server-filesystem /tmp

# 添加自定义服务器
python cli.py add-mcp-server demo-server python demo_server.py --env TZ=Asia/Shanghai DEBUG=true
```

### MCP 配置文件格式

CLI 支持标准的 JSON 格式和带注释的 JSONC 格式：

```json
{
  "mcpServers": {
    "文件系统服务器": {
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "env": {
        "TZ": "Asia/Shanghai"
      },
      "description": "文件系统操作工具"
    },
    
    "时间服务": {
      "command": ["python", "./time_service.py"],
      "timeout": 30,
      "env": {
        "TZ": "Asia/Shanghai"
      },
      "description": "时间相关功能"
    },
    
    "天气服务": {
      "command": ["python", "./weather_service.py"],
      "timeout": 60,
      "env": {
        "API_KEY": "your-weather-api-key",
        "TZ": "Asia/Shanghai"
      },
      "description": "天气查询服务"
    }
  },
  
  "全局环境变量": {
    "TZ": "Asia/Shanghai",
    "LANG": "zh_CN.UTF-8"
  }
}
```

#### 配置文件字段说明

- `command`: 启动 MCP 服务器的命令和参数（数组格式）
- `timeout`: 请求超时时间（秒）
- `env`: 环境变量（可选）
- `description`: 服务器描述（可选，仅用于文档）

#### 支持的格式

1. **标准 JSON**: 不带注释的 JSON 文件
2. **JSONC**: 带 `//` 单行注释和 `/* */` 多行注释的 JSON 文件
3. **直接格式**: 不需要 `mcpServers` 包装的格式

## 交互式对话

### 启动聊天

```bash
python cli.py chat
```

在聊天模式中：
- 输入 `quit` 或 `exit` 退出
- BaseAgent 将根据上下文自动选择使用技能或 MCP 工具
- 支持多轮对话，记住上下文

### 示例对话

```
You: What time is it now?
Agent: I'll use the time service to get the current time for you.

You: Calculate 15% of 200
Agent: 15% of 200 = 0.15 × 200 = 30

You: Read the contents of /tmp/test.txt
Agent: I'll use the filesystem tool to read that file for you.
```

## 完整工作流示例

### 1. 初始化和配置

```bash
# 查看帮助和示例
python cli.py examples

# 查看当前状态
python cli.py info

# 列出默认技能
python cli.py list-skills
```

### 2. 设置 MCP 服务器

```bash
# 生成示例配置
python cli.py generate-config --output mcp-config.json

# 编辑配置文件（添加你的 API 密钥等）
# vim mcp-config.json

# 加载配置
python cli.py load-mcp-config mcp-config.json

# 验证服务器
python cli.py list-mcp
```

### 3. 添加自定义技能

```bash
# 创建技能指令文件
cat > my_skill.md << 'EOF'
# 我的技能

你是一个专业的助手，能够...

## 能力
- 能力1
- 能力2

## 使用指南
- 指南1
- 指南2
EOF

# 添加技能
python cli.py add-skill "my-skill" "描述我的技能" my_skill.md --tags tag1 tag2
```

### 4. 开始使用

```bash
# 开始对话
python cli.py chat
```

## 故障排除

### 常见问题

1. **API 密钥未设置**
   ```
   Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.
   ```
   解决方案：设置 `OPENAI_API_KEY` 环境变量

2. **MCP 服务器启动失败**
   ```
   Failed to register MCP server 'server-name': ...
   ```
   解决方案：检查命令路径、权限和依赖

3. **技能文件不存在**
   ```
   Error: Instructions file 'file.md' not found
   ```
   解决方案：确保文件路径正确

### 调试模式

```bash
# 查看详细错误信息
python cli.py list-mcp

# 检查配置文件语法
python -m json.tool mcp-config.json

# 测试 MCP 服务器
python your_mcp_server.py
```

## 高级功能

### 自定义 MCP 服务器开发

参考 `time_service.py` 示例实现你自己的 MCP 服务器：

```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime

async def handle_request(request):
    # 处理 JSON-RPC 请求
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "initialize":
        return initialize_response()
    elif method == "tools/list":
        return tools_list_response()
    elif method == "tools/call":
        return tools_call_response(params)
    
    return error_response(f"Method {method} not found")

def initialize_response():
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "your-server", "version": "1.0.0"}
        }
    }

def tools_list_response():
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": [
                {
                    "name": "your_tool",
                    "description": "Your tool description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string"}
                        }
                    }
                }
            ]
        }
    }

if __name__ == "__main__":
    # 读取标准输入，处理请求，输出响应
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        
        request = json.loads(line.strip())
        response = handle_request(request)
        print(json.dumps(response))
        sys.stdout.flush()
```

## 演示脚本

运行完整的功能演示：

```bash
python demo_cli.py
```

这个脚本会演示所有主要功能，包括：
- 查看帮助和示例
- 生成配置文件
- 添加 MCP 服务器和技能
- 查看最终状态

## 总结

BaseAgent CLI 提供了完整的命令行界面来使用 BaseAgent 的所有功能：

- ✅ 交互式对话
- ✅ 技能管理（Anthropic Skills 格式）
- ✅ MCP 服务器管理（JSON/JSONC 配置）
- ✅ 配置生成和示例
- ✅ 状态监控和调试

开始使用：运行 `python cli.py examples` 查看完整的使用示例。