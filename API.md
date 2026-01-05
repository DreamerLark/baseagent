# BaseAgent API Documentation

## Overview

BaseAgent provides a REST API that allows you to interact with an AI agent using OpenAI format, with support for Skills and MCP (Model Context Protocol).

Base URL: `http://localhost:8000`

## Authentication

Currently, no authentication is required for API endpoints. The OpenAI API key is configured server-side via environment variables.

## Endpoints

### Health Check

#### GET /

Returns basic API information.

**Response:**
```json
{
  "name": "BaseAgent API",
  "version": "1.0.0",
  "description": "An AI agent with OpenAI API format supporting MCP and skills"
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Chat Endpoints

#### POST /chat

Send a message to the agent and receive a response.

**Request Body:**
```json
{
  "message": "What is 25 + 17?",
  "stream": false
}
```

**Parameters:**
- `message` (string, required): The message to send to the agent
- `stream` (boolean, optional): Enable streaming response (default: false)

**Response:**
```json
{
  "response": "The result of 25 + 17 is 42.",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is 25 + 17?"
    },
    {
      "role": "assistant",
      "content": "The result of 25 + 17 is 42."
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 15 * 8"}'
```

#### POST /chat/reset

Reset the conversation history.

**Response:**
```json
{
  "status": "conversation reset"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/chat/reset
```

#### GET /conversation

Get the current conversation history.

**Response:**
```json
{
  "conversation_history": [...]
}
```

**Example:**
```bash
curl http://localhost:8000/conversation
```

---

### Skills Endpoints

#### GET /skills

List all available skills.

**Response:**
```json
{
  "skills": {
    "calculate": {
      "description": "Perform arithmetic calculations",
      "parameters": {
        "type": "object",
        "properties": {
          "operation": {
            "type": "string",
            "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"]
          },
          "a": {"type": "number"},
          "b": {"type": "number"}
        },
        "required": ["operation", "a"]
      }
    },
    "get_current_time": {...},
    "read_file": {...},
    "write_file": {...},
    "search_text": {...}
  }
}
```

**Example:**
```bash
curl http://localhost:8000/skills
```

#### POST /skills/execute

Execute a skill directly without going through the agent.

**Request Body:**
```json
{
  "skill_name": "calculate",
  "arguments": {
    "operation": "multiply",
    "a": 15,
    "b": 8
  }
}
```

**Response:**
```json
{
  "result": {
    "result": 120
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "calculate",
    "arguments": {
      "operation": "add",
      "a": 10,
      "b": 5
    }
  }'
```

#### POST /skills/register

Register a new skill (Note: This registers the skill configuration, but the actual function must be implemented server-side).

**Request Body:**
```json
{
  "name": "my_custom_skill",
  "description": "A custom skill description",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string"}
    },
    "required": ["param1"]
  }
}
```

**Response:**
```json
{
  "status": "skill registered",
  "name": "my_custom_skill"
}
```

---

### MCP (Model Context Protocol) Endpoints

#### POST /mcp/servers

Add a new MCP server.

**Request Body:**
```json
{
  "name": "filesystem",
  "server_url": "http://localhost:3000",
  "timeout": 30
}
```

**Parameters:**
- `name` (string, required): Name identifier for the MCP server
- `server_url` (string, required): URL of the MCP server
- `timeout` (integer, optional): Request timeout in seconds (default: 30)

**Response:**
```json
{
  "status": "MCP server added",
  "name": "filesystem",
  "server_url": "http://localhost:3000"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_server",
    "server_url": "http://localhost:3000"
  }'
```

#### GET /mcp/servers

List all registered MCP servers.

**Response:**
```json
{
  "servers": ["filesystem", "database", "weather"]
}
```

**Example:**
```bash
curl http://localhost:8000/mcp/servers
```

#### GET /mcp/tools

List all tools available from all registered MCP servers.

**Response:**
```json
{
  "tools": {
    "filesystem": [
      {
        "name": "read_file",
        "description": "Read a file from the filesystem",
        "parameters": {...}
      }
    ],
    "database": [...]
  }
}
```

**Example:**
```bash
curl http://localhost:8000/mcp/tools
```

#### POST /mcp/tools/call

Call a tool from a specific MCP server.

**Request Body:**
```json
{
  "server_name": "filesystem",
  "tool_name": "read_file",
  "arguments": {
    "path": "/path/to/file.txt"
  }
}
```

**Response:**
```json
{
  "result": {
    "content": "File contents here...",
    "size": 1024
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "filesystem",
    "tool_name": "list_directory",
    "arguments": {"path": "/tmp"}
  }'
```

---

## Built-in Skills

### 1. calculate

Perform arithmetic operations.

**Parameters:**
- `operation`: "add", "subtract", "multiply", "divide", "power", or "sqrt"
- `a`: First number
- `b`: Second number (not required for sqrt)

**Example:**
```json
{
  "skill_name": "calculate",
  "arguments": {
    "operation": "multiply",
    "a": 7,
    "b": 6
  }
}
```

### 2. get_current_time

Get the current date and time.

**Parameters:**
- `timezone`: (optional) Timezone name

**Example:**
```json
{
  "skill_name": "get_current_time",
  "arguments": {}
}
```

### 3. read_file

Read contents from a file.

**Parameters:**
- `filepath`: Path to the file

**Example:**
```json
{
  "skill_name": "read_file",
  "arguments": {
    "filepath": "/path/to/file.txt"
  }
}
```

### 4. write_file

Write contents to a file.

**Parameters:**
- `filepath`: Path to the file
- `content`: Content to write

**Example:**
```json
{
  "skill_name": "write_file",
  "arguments": {
    "filepath": "/tmp/output.txt",
    "content": "Hello, World!"
  }
}
```

### 5. search_text

Search for text in a given content.

**Parameters:**
- `text`: The text to search in
- `query`: The search query
- `case_sensitive`: (optional) Boolean, default false

**Example:**
```json
{
  "skill_name": "search_text",
  "arguments": {
    "text": "Hello World, this is a test",
    "query": "World"
  }
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server error

Error responses have the following format:
```json
{
  "detail": "Error message here"
}
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

Visit `http://localhost:8000/redoc` for ReDoc documentation.
