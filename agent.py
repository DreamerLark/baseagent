import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseAgent:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4-turbo-preview"
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
        
        self.conversation_history: List[Dict[str, Any]] = []
        self.skills: Dict[str, callable] = {}
        self.mcp_servers: Dict[str, Any] = {}
        
    def register_skill(self, name: str, func: callable, description: str, parameters: Dict[str, Any]):
        self.skills[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
        
    def register_mcp_server(self, name: str, server_config: Dict[str, Any]):
        self.mcp_servers[name] = server_config
        
    def _convert_skills_to_tools(self) -> List[Dict[str, Any]]:
        tools = []
        for skill_name, skill_info in self.skills.items():
            tool = {
                "type": "function",
                "function": {
                    "name": skill_name,
                    "description": skill_info["description"],
                    "parameters": skill_info["parameters"]
                }
            }
            tools.append(tool)
        return tools
    
    def _execute_skill(self, skill_name: str, arguments: Dict[str, Any]) -> Any:
        if skill_name not in self.skills:
            return {"error": f"Skill '{skill_name}' not found"}
        
        try:
            skill_func = self.skills[skill_name]["function"]
            result = skill_func(**arguments)
            return result
        except Exception as e:
            return {"error": f"Error executing skill '{skill_name}': {str(e)}"}
    
    def _call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if server_name not in self.mcp_servers:
            return {"error": f"MCP server '{server_name}' not found"}
        
        try:
            server = self.mcp_servers[server_name]
            if "client" in server and hasattr(server["client"], "call_tool"):
                result = server["client"].call_tool(tool_name, arguments)
                return result
            else:
                return {"error": f"MCP server '{server_name}' does not support tool calls"}
        except Exception as e:
            return {"error": f"Error calling MCP tool '{tool_name}': {str(e)}"}
    
    def chat(self, message: str, stream: bool = False) -> str:
        if not self.client:
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
        
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        tools = self._convert_skills_to_tools()
        
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
                    
                    function_response = self._execute_skill(function_name, function_args)
                    
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
    
    def reset_conversation(self):
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self.conversation_history


if __name__ == "__main__":
    agent = BaseAgent()
    
    def calculate(operation: str, a: float, b: float) -> Dict[str, Any]:
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }
        
        if operation in operations:
            result = operations[operation](a, b)
            return {"result": result}
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    agent.register_skill(
        name="calculate",
        func=calculate,
        description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "The first number"
                },
                "b": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "a", "b"]
        }
    )
    
    print("BaseAgent initialized. Type 'quit' to exit.")
    print("Example: What is 25 + 17?")
    print()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        response = agent.chat(user_input)
        print(f"Agent: {response}")
        print()
