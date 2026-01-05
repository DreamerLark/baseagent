import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import BaseAgent
from skills import SkillRegistry
from mcp_client import MCPManager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BaseAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = BaseAgent()
skill_registry = SkillRegistry()
mcp_manager = MCPManager()

for skill_name, skill_info in skill_registry.get_all_skills().items():
    agent.register_skill(
        name=skill_name,
        func=lambda **kwargs: skill_registry.execute(skill_name, **kwargs),
        description=skill_info["description"],
        parameters=skill_info["parameters"]
    )


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


class MCPServerRequest(BaseModel):
    name: str
    server_url: str
    timeout: int = 30


class MCPToolRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]


@app.get("/")
def root():
    return {
        "name": "BaseAgent API",
        "version": "1.0.0",
        "description": "An AI agent with OpenAI API format supporting MCP and skills"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = agent.chat(request.message, stream=request.stream)
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
def list_skills():
    return {"skills": skill_registry.get_all_skills()}


@app.post("/skills/execute", response_model=SkillResponse)
def execute_skill(request: SkillRequest):
    try:
        result = skill_registry.execute(request.skill_name, **request.arguments)
        return SkillResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/skills/register")
def register_skill(name: str, description: str, parameters: Dict[str, Any]):
    try:
        agent.register_skill(
            name=name,
            func=lambda **kwargs: skill_registry.execute(name, **kwargs),
            description=description,
            parameters=parameters
        )
        return {"status": "skill registered", "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/servers")
def add_mcp_server(request: MCPServerRequest):
    try:
        client = mcp_manager.add_server(
            name=request.name,
            server_url=request.server_url,
            timeout=request.timeout
        )
        agent.register_mcp_server(request.name, {"client": client})
        return {
            "status": "MCP server added",
            "name": request.name,
            "server_url": request.server_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/servers")
def list_mcp_servers():
    return {"servers": list(mcp_manager.servers.keys())}


@app.get("/mcp/tools")
def list_mcp_tools():
    try:
        tools = mcp_manager.list_all_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/call")
def call_mcp_tool(request: MCPToolRequest):
    try:
        result = mcp_manager.call_tool(
            server_name=request.server_name,
            tool_name=request.tool_name,
            arguments=request.arguments
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
