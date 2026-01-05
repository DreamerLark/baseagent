# BaseAgent 快速参考

## 安装

```bash
./setup.sh
# 或
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## 配置

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

## 运行

### 方式 1：命令行
```bash
python example_usage.py
```

### 方式 2：API 服务器
```bash
python server.py
# 访问 http://localhost:8000/docs
```

### 方式 3：Docker
```bash
docker-compose up
```

## 代码示例

### 基础对话
```python
from agent import BaseAgent

agent = BaseAgent()
response = agent.chat("计算 25 + 17")
print(response)
```

### 注册技能
```python
def my_skill(param: str) -> dict:
    return {"result": param.upper()}

agent.register_skill(
    name="my_skill",
    func=my_skill,
    description="转换为大写",
    parameters={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
)
```

### 使用 MCP
```python
from mcp_client import MCPManager

mcp_manager = MCPManager()
client = mcp_manager.add_server("server", "http://localhost:3000")
agent.register_mcp_server("server", {"client": client})
```

## API 调用

### 发送消息
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

### 执行技能
```bash
curl -X POST http://localhost:8000/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "calculate", "arguments": {"operation": "add", "a": 1, "b": 2}}'
```

### 查看技能
```bash
curl http://localhost:8000/skills
```

## 内置技能

| 技能 | 功能 | 示例 |
|------|------|------|
| calculate | 数学计算 | `{"operation": "add", "a": 1, "b": 2}` |
| get_current_time | 获取时间 | `{}` |
| read_file | 读取文件 | `{"filepath": "/path/to/file"}` |
| write_file | 写入文件 | `{"filepath": "/path", "content": "text"}` |
| search_text | 搜索文本 | `{"text": "...", "query": "..."}` |

## 测试

```bash
python test_agent.py
```

## 文档

- 完整文档：`README.md`
- 中文指南：`使用指南.md`
- API 文档：`API.md`
- 实现说明：`IMPLEMENTATION.md`

## 帮助

访问 http://localhost:8000/docs 查看交互式 API 文档
