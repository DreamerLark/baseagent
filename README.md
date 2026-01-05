# BaseAgent

一个基于 OpenAI API 格式的 AI Agent，支持调用 MCP (Model Context Protocol) 和 Skills。

## 功能特性

- ✅ 使用 OpenAI 格式的 API 进行对话
- ✅ 支持自定义 Skills (技能) 注册和调用
- ✅ 支持 MCP (Model Context Protocol) 服务器集成
- ✅ 内置多个默认技能：计算、文件读写、文本搜索、获取时间等
- ✅ 提供 REST API 服务器
- ✅ 支持对话历史管理
- ✅ Function Calling 自动处理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
PORT=8000
```

### 3. 运行示例

#### 命令行模式

```bash
python agent.py
```

#### 示例脚本

```bash
python example_usage.py
```

#### API 服务器模式

```bash
python server.py
```

或使用 uvicorn：

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## 使用方法

### 1. 基础用法

```python
from agent import BaseAgent

# 创建 agent 实例
agent = BaseAgent()

# 开始对话
response = agent.chat("你好，请帮我计算 25 + 17")
print(response)
```

### 2. 注册自定义 Skill

```python
from agent import BaseAgent

agent = BaseAgent()

# 定义技能函数
def get_weather(city: str) -> dict:
    # 这里可以调用真实的天气 API
    return {
        "city": city,
        "temperature": 25,
        "condition": "晴天"
    }

# 注册技能
agent.register_skill(
    name="get_weather",
    func=get_weather,
    description="获取指定城市的天气信息",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            }
        },
        "required": ["city"]
    }
)

# 使用技能
response = agent.chat("北京今天天气怎么样？")
print(response)
```

### 3. 集成 MCP 服务器

```python
from agent import BaseAgent
from mcp_client import MCPManager

agent = BaseAgent()
mcp_manager = MCPManager()

# 添加 MCP 服务器
client = mcp_manager.add_server(
    name="my_mcp_server",
    server_url="http://localhost:3000"
)

# 注册到 agent
agent.register_mcp_server("my_mcp_server", {"client": client})

# 现在可以通过 agent 调用 MCP 工具
```

### 4. 使用 REST API

启动服务器后，可以通过 HTTP 请求与 agent 交互：

#### 发送对话消息

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 15 * 8"}'
```

#### 列出所有技能

```bash
curl http://localhost:8000/skills
```

#### 直接执行技能

```bash
curl -X POST http://localhost:8000/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "calculate",
    "arguments": {
      "operation": "multiply",
      "a": 15,
      "b": 8
    }
  }'
```

#### 添加 MCP 服务器

```bash
curl -X POST http://localhost:8000/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_server",
    "server_url": "http://localhost:3000"
  }'
```

#### 查看 API 文档

访问 `http://localhost:8000/docs` 查看完整的 API 文档（Swagger UI）。

## 内置技能

BaseAgent 默认包含以下技能：

1. **get_current_time** - 获取当前时间
2. **calculate** - 执行数学计算（加、减、乘、除、幂、平方根）
3. **read_file** - 读取文件内容
4. **write_file** - 写入文件内容
5. **search_text** - 在文本中搜索

## 项目结构

```
baseagent/
├── agent.py              # 核心 Agent 实现
├── skills.py             # 技能注册和管理
├── mcp_client.py         # MCP 客户端实现
├── server.py             # FastAPI 服务器
├── example_usage.py      # 使用示例
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量模板
├── .gitignore           # Git 忽略文件
└── README.md            # 项目文档
```

## MCP (Model Context Protocol)

MCP 是一个用于 AI 应用与外部工具和数据源通信的协议。本项目支持连接到 MCP 服务器，使 AI agent 能够：

- 调用远程工具和函数
- 访问外部数据资源
- 与其他服务集成

### MCP 服务器示例

```python
from mcp_client import MCPManager

mcp_manager = MCPManager()

# 添加服务器
mcp_manager.add_server(
    name="filesystem",
    server_url="http://localhost:3000"
)

# 列出所有工具
tools = mcp_manager.list_all_tools()
print(tools)

# 调用工具
result = mcp_manager.call_tool(
    server_name="filesystem",
    tool_name="read_file",
    arguments={"path": "/path/to/file"}
)
print(result)
```

## 开发指南

### 添加新技能

1. 在 `skills.py` 中定义技能函数
2. 在 `SkillRegistry._register_default_skills()` 中注册
3. 重启 agent 或服务器

### 自定义 Agent 行为

可以继承 `BaseAgent` 类并重写方法来自定义行为：

```python
from agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def chat(self, message: str, stream: bool = False) -> str:
        # 添加自定义逻辑
        print(f"Processing: {message}")
        return super().chat(message, stream)
```

## API 端点

### Chat

- `POST /chat` - 发送消息并获取回复
- `POST /chat/reset` - 重置对话历史
- `GET /conversation` - 获取对话历史

### Skills

- `GET /skills` - 列出所有技能
- `POST /skills/execute` - 直接执行技能
- `POST /skills/register` - 注册新技能

### MCP

- `POST /mcp/servers` - 添加 MCP 服务器
- `GET /mcp/servers` - 列出所有 MCP 服务器
- `GET /mcp/tools` - 列出所有 MCP 工具
- `POST /mcp/tools/call` - 调用 MCP 工具

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
