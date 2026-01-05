import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from skills import SkillRegistry
from mcp_client import MCPManager

load_dotenv()


class BaseAgent:
    """
    BaseAgent with support for AgentSkills and MCP
    - Skills: Following https://agentskills.io/home specification
    - MCP: Following https://modelcontextprotocol.io/docs/getting-started/intro specification
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4-turbo-preview"
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
        
        self.conversation_history: List[Dict[str, Any]] = []
        self.skill_registry = SkillRegistry()
        self.mcp_manager = MCPManager()
        
    async def register_skill(
        self,
        name: str,
        description: str,
        instructions: str,
        version: str = "1.0.0",
        category = None,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        guidelines: Optional[List[str]] = None
    ):
        """Register a new skill following Anthropic Skills specification"""
        from skills import SkillCategory
        if category is None:
            category = SkillCategory.CUSTOM
            
        self.skill_registry.register_skill(
            name=name,
            description=description,
            instructions=instructions,
            version=version,
            category=category,
            tags=tags,
            examples=examples,
            guidelines=guidelines
        )
        
    async def register_mcp_server(self, name: str, command: List[str], timeout: int = 30):
        """
        Register an MCP server following MCP specification
        
        Args:
            name: Server name
            command: Command to start the MCP server (e.g., ["python", "server.py"])
            timeout: Request timeout
        """
        await self.mcp_manager.add_server(name, command, timeout)
        
    def _convert_skills_to_tools(self) -> List[Dict[str, Any]]:
        """Convert AgentSkills to OpenAI function calling format"""
        return self.skill_registry.to_openai_tools()
        
    async def _execute_skill(self, skill_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill by name - return skill instructions for AI guidance"""
        skill = self.skill_registry.get_skill(skill_name)
        
        if not skill:
            return {"error": f"Skill '{skill_name}' not found"}
        
        # For Anthropic Skills, we return the skill information
        # The AI will use this information to guide its behavior
        return {
            "skill_name": skill_name,
            "description": skill.frontmatter.description,
            "instructions": skill.frontmatter.instructions,
            "category": skill.frontmatter.category,
            "tags": skill.frontmatter.tags,
            "examples": skill.frontmatter.examples,
            "guidelines": skill.frontmatter.guidelines,
            "message": f"Skill '{skill_name}' is now active. Follow the instructions provided."
        }
            
    async def _call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on an MCP server"""
        try:
            result = await self.mcp_manager.call_tool(server_name, tool_name, arguments)
            return result
        except Exception as e:
            return {"error": f"Error calling MCP tool '{tool_name}' on server '{server_name}': {str(e)}"}
            
    async def _convert_mcp_tools_to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function calling format"""
        all_tools = await self.mcp_manager.list_all_tools()
        openai_tools = []
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": f"{server_name}_{tool.get('name', '')}",
                        "description": f"[MCP:{server_name}] {tool.get('description', '')}",
                        "parameters": tool.get('inputSchema', {})
                    }
                }
                openai_tools.append(openai_tool)
                
        return openai_tools
        
    async def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from OpenAI, routing to either skills or MCP"""
        # Check if it's an MCP tool (prefix format: servername_toolname)
        if "_" in tool_name:
            parts = tool_name.split("_", 1)
            if parts[0] in self.mcp_manager.clients:
                return await self._call_mcp_tool(parts[0], parts[1], arguments)
        
        # Otherwise, it's a skill
        return await self._execute_skill(tool_name, arguments)
        
    async def chat(self, message: str, stream: bool = False) -> str:
        """
        Chat with the agent
        
        Args:
            message: User message
            stream: Whether to stream the response (not yet implemented)
            
        Returns:
            Agent response
        """
        if not self.client:
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
        
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Get skills and MCP tools
        skill_tools = self._convert_skills_to_tools()
        mcp_tools = await self._convert_mcp_tools_to_openai_format()
        tools = skill_tools + mcp_tools
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            kwargs = {
                "model": self.model,
                "messages": self.conversation_history,
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            assistant_message = response.choices[0].message
            
            if assistant_message.tool_calls:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })
                
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Handle the tool call asynchronously
                    function_response = await self._handle_tool_call(function_name, function_args)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_response)
                    })
                
                continue
            else:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content
                })
                return assistant_message.content
        
        return "Max iterations reached. The agent could not complete the task."
    
    def chat_sync(self, message: str, stream: bool = False) -> str:
        """Synchronous wrapper for chat method"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.chat(message, stream))
            finally:
                loop.close()
        else:
            return loop.run_until_complete(self.chat(message, stream))
        
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history
        
    async def list_all_skills(self) -> Dict[str, Any]:
        """List all available skills"""
        return {
            "skills": self.skill_registry.get_all_skills(),
            "mcp_servers": list(self.mcp_manager.clients.keys())
        }
        
    async def list_all_tools(self) -> Dict[str, Any]:
        """List all available tools (skills + MCP tools)"""
        skills = self.skill_registry.get_all_skills()
        mcp_tools = await self.mcp_manager.list_all_tools()
        
        return {
            "skills": skills,
            "mcp_tools": mcp_tools
        }
        
    async def close(self):
        """Clean up resources"""
        await self.mcp_manager.close_all()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = BaseAgent()
        
        # Register a calculator skill following Anthropic Skills spec
        await agent.register_skill(
            name="calculator",
            description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
            instructions="""You are a calculator assistant. Perform accurate mathematical calculations and provide clear, step-by-step explanations when helpful.

For calculations:
- Show your work for complex problems
- Round results to appropriate precision
- Check for edge cases (division by zero, negative numbers, etc.)
- Use standard mathematical notation

Supported operations:
- Basic arithmetic: +, -, *, /
- Advanced: power (^), square root (√)
- Order of operations applies

Example responses:
- "2 + 3 = 5"
- "For 15% of 80: 0.15 × 80 = 12"
""",
            category=SkillCategory.UTILITIES,
            tags=["arithmetic", "basic", "math"],
            examples=[
                "What's 15% of 80?",
                "Calculate 2^10",
                "What is the square root of 144?"
            ],
            guidelines=[
                "Show work for complex calculations",
                "Use appropriate precision",
                "Check for edge cases"
            ]
        )
        
        print("BaseAgent initialized with Anthropic Skills. Type 'quit' to exit.")
        print("Example: What is 25 + 17?")
        print()
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            
            response = await agent.chat(user_input)
            print(f"Agent: {response}")
            print()
        
        await agent.close()
    
    asyncio.run(main())
