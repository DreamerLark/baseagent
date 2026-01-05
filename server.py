import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import BaseAgent
from skills import SkillCategory
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BaseAgent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = BaseAgent()


class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, Any]]


class SkillRequest(BaseModel):
    skill_name: str
    arguments: Dict[str, Any]


class SkillResponse(BaseModel):
    result: Any


class RegisterSkillRequest(BaseModel):
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    author: str = "baseagent"
    category: str = "custom"
    tags: Optional[List[str]] = None
    documentation: Optional[str] = None


class MCPServerRequest(BaseModel):
    name: str
    command: List[str]
    timeout: int = 30


class MCPToolRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]


@app.get("/")
def root():
    return {
        "name": "BaseAgent API",
        "version": "2.0.0",
        "description": "An AI agent with AgentSkills and MCP support",
        "specifications": {
            "skills": "https://agentskills.io/home",
            "mcp": "https://modelcontextprotocol.io/docs/getting-started/intro"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await agent.chat(request.message, stream=request.stream)
        return ChatResponse(
            response=response,
            conversation_history=agent.get_conversation_history()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/reset")
def reset_chat():
    agent.reset_conversation()
    return {"status": "conversation reset"}


@app.get("/conversation")
def get_conversation():
    return {"conversation_history": agent.get_conversation_history()}


@app.get("/skills")
async def list_skills():
    skills_info = await agent.list_all_skills()
    return skills_info


@app.post("/skills/execute", response_model=SkillResponse)
async def execute_skill(request: SkillRequest):
    try:
        result = await agent.skill_registry.execute(request.skill_name, **request.arguments)
        if result.success:
            return SkillResponse(result=result.data)
        else:
            raise HTTPException(status_code=400, detail=result.error)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/skills/register")
async def register_skill(request: RegisterSkillRequest):
    try:
        # Convert category string to enum
        category = SkillCategory.CUSTOM
        if request.category:
            try:
                category = SkillCategory(request.category)
            except ValueError:
                category = SkillCategory.CUSTOM
        
        # Note: For API registration, we need to store the function separately
        # This is a simplified version - in production you'd want a way to load functions dynamically
        return {
            "status": "skill registration via API requires function implementation",
            "message": "Use the Python API to register skills with custom functions",
            "name": request.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/servers")
async def add_mcp_server(request: MCPServerRequest):
    try:
        await agent.register_mcp_server(
            name=request.name,
            command=request.command,
            timeout=request.timeout
        )
        return {
            "status": "MCP server added",
            "name": request.name,
            "command": request.command
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/servers")
async def list_mcp_servers():
    skills_info = await agent.list_all_skills()
    return {"servers": skills_info.get("mcp_servers", [])}


@app.get("/mcp/tools")
async def list_mcp_tools():
    try:
        tools_info = await agent.list_all_tools()
        return {"tools": tools_info.get("mcp_tools", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/call")
async def call_mcp_tool(request: MCPToolRequest):
    try:
        result = await agent._call_mcp_tool(
            server_name=request.server_name,
            tool_name=request.tool_name,
            arguments=request.arguments
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_all_tools():
    """List all available tools (skills + MCP tools)"""
    try:
        tools_info = await agent.list_all_tools()
        return tools_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    await agent.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
