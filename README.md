# BaseAgent

A minimal AI agent designed to test and demonstrate skill support, following both AgentSkills and Model Context Protocol (MCP) specifications.

## Specifications

- **AgentSkills**: Following the specification at https://agentskills.io/home
- **MCP**: Following the specification at https://modelcontextprotocol.io/docs/getting-started/intro

## Features

- ✅ AgentSkills implementation with proper manifests and versioning
- ✅ MCP (Model Context Protocol) client with JSON-RPC 2.0 over stdio
- ✅ OpenAI API format with function calling support
- ✅ Built-in skills for common operations
- ✅ Async/await support throughout
- ✅ REST API server with FastAPI

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Setup with the setup script
bash setup.sh
```

### Basic Usage

```python
import asyncio
from agent import BaseAgent

async def main():
    agent = BaseAgent()
    
    # List available skills
    skills_info = await agent.list_all_skills()
    print(f"Available skills: {list(skills_info['skills'].keys())}")
    
    # Execute a skill directly
    result = await agent.skill_registry.execute("calculate", operation="add", a=5, b=3)
    if result.success:
        print(f"Result: {result.data['result']}")
    
    # Chat with the agent
    response = await agent.chat("What is 25 + 17?")
    print(f"Agent: {response}")
    
    await agent.close()

asyncio.run(main())
```

## AgentSkills Implementation

### Skill Manifest

Each skill follows the AgentSkills specification with a complete manifest:

```python
from skills import SkillCategory

agent.register_skill(
    name="my_skill",
    version="1.0.0",
    description="Description of what the skill does",
    func=my_function,
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"}
        },
        "required": ["param1"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "result": {"type": "string"}
        }
    },
    author="your-name",
    category=SkillCategory.CUSTOM,
    tags=["custom", "tag"]
)
```

### Skill Categories

- `UTILITIES` - Utility functions
- `MATH` - Mathematical operations
- `FILE_OPERATIONS` - File I/O operations
- `TEXT_PROCESSING` - Text manipulation
- `DATA_MANIPULATION` - Data processing
- `COMMUNICATION` - Communication tools
- `ANALYSIS` - Analysis tools
- `CUSTOM` - Custom user-defined skills

### Built-in Skills

1. **calculate** - Perform arithmetic operations (add, subtract, multiply, divide, power, sqrt)
2. **get_current_time** - Get current date and time
3. **read_file** - Read file contents
4. **write_file** - Write content to file
5. **search_text** - Search for text within content

## MCP Implementation

### Adding an MCP Server

```python
# MCP servers use stdio and JSON-RPC 2.0
await agent.register_mcp_server(
    name="filesystem",
    command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
)

# MCP tools are automatically available to the agent
response = await agent.chat("Read the file README.md")
```

### MCP Features

- JSON-RPC 2.0 protocol over stdio
- Initialization handshake with capabilities exchange
- Tools, resources, and prompts support
- Automatic conversion to OpenAI function calling format
- Multiple MCP server management

## REST API

Start the API server:

```bash
python server.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /chat` - Chat with the agent
- `GET /skills` - List all available skills
- `POST /skills/execute` - Execute a skill
- `POST /mcp/servers` - Add an MCP server
- `GET /mcp/tools` - List MCP tools
- `POST /mcp/tools/call` - Call an MCP tool
- `GET /tools` - List all tools (skills + MCP)

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Examples

### Example 1: Using Skills

```python
import asyncio
from agent import BaseAgent
from skills import SkillCategory

async def main():
    agent = BaseAgent()
    
    # Register a custom skill
    def get_weather(city: str) -> dict:
        return {"city": city, "temperature": 22, "condition": "Sunny"}
    
    await agent.register_skill(
        name="get_weather",
        version="1.0.0",
        description="Get weather for a city",
        func=get_weather,
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "temperature": {"type": "number"},
                "condition": {"type": "string"}
            }
        },
        category=SkillCategory.CUSTOM,
        tags=["weather"]
    )
    
    # Use the skill
    result = await agent.skill_registry.execute("get_weather", city="Beijing")
    print(result.data)
    
    await agent.close()

asyncio.run(main())
```

### Example 2: Using MCP

```python
import asyncio
from agent import BaseAgent

async def main():
    agent = BaseAgent()
    
    # Add an MCP filesystem server
    await agent.register_mcp_server(
        name="filesystem",
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    )
    
    # Chat with the agent - it will use MCP tools automatically
    response = await agent.chat("What files are in the documents folder?")
    print(response)
    
    await agent.close()

asyncio.run(main())
```

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
PORT=8000
```

## Testing

Run the test suite:

```bash
python test_agent.py
```

## Docker

Build and run with Docker:

```bash
docker build -t baseagent .
docker run -p 8000:8000 --env-file .env baseagent
```

Or use Docker Compose:

```bash
docker-compose up
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  REST API Server                 │
│                   (server.py)                    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│               BaseAgent (agent.py)               │
│  - OpenAI Client                                 │
│  - Conversation Management                       │
│  - Function Calling Handler                      │
└──────────────┬────────────────┬──────────────────┘
               │                │
               ▼                ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  SkillRegistry   │  │   MCPManager     │
    │   (skills.py)    │  │ (mcp_client.py)  │
    │  AgentSkills     │  │  MCP Protocol    │
    │  Specification   │  │  JSON-RPC 2.0    │
    └──────────────────┘  └──────────────────┘
               │                │
               ▼                ▼
        [Built-in Skills]  [MCP Servers]
        - calculate         - filesystem
        - read_file         - database
        - write_file        - custom...
        - search_text
        - get_time
```

## Documentation

- [API Documentation](API.md) - Detailed API reference
- [Implementation Guide](IMPLEMENTATION.md) - Implementation details
- [Quick Start Guide](QUICKSTART.md) - Quick start instructions
- [使用指南](使用指南.md) - Chinese user guide

## Specifications Compliance

### AgentSkills

✅ Skill manifests with versioning
✅ JSON Schema for input/output
✅ Skill categories and tags
✅ Metadata (author, license, documentation)
✅ Execution results with timing

### MCP

✅ JSON-RPC 2.0 protocol
✅ stdio communication
✅ Initialization handshake
✅ Capabilities exchange
✅ Tools, resources, and prompts support

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

This is a minimal agent for testing skill support. Contributions should focus on:
- Maintaining AgentSkills specification compliance
- Maintaining MCP specification compliance
- Adding new built-in skills
- Improving documentation
