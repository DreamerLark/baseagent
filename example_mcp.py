from agent import BaseAgent
from skills import SkillRegistry
from mcp_client import MCPManager


def main():
    print("=== BaseAgent with MCP Integration Example ===\n")
    
    agent = BaseAgent()
    skill_registry = SkillRegistry()
    mcp_manager = MCPManager()
    
    print("Step 1: Registering default skills...")
    for skill_name, skill_info in skill_registry.get_all_skills().items():
        agent.register_skill(
            name=skill_name,
            func=lambda sn=skill_name, **kwargs: skill_registry.execute(sn, **kwargs),
            description=skill_info["description"],
            parameters=skill_info["parameters"]
        )
    print(f"Registered {len(skill_registry.get_all_skills())} skills\n")
    
    print("Step 2: Setting up MCP servers...")
    print("Note: To use real MCP servers, uncomment and configure below:")
    print("# mcp_manager.add_server('filesystem', 'http://localhost:3000')")
    print("# agent.register_mcp_server('filesystem', {'client': mcp_manager.get_server('filesystem')})")
    print()
    
    print("Step 3: Adding a custom weather skill as example...")
    def get_weather(city: str, unit: str = "celsius") -> dict:
        return {
            "city": city,
            "temperature": 22,
            "unit": unit,
            "condition": "Sunny",
            "humidity": 65,
            "wind_speed": 10
        }
    
    agent.register_skill(
        name="get_weather",
        func=get_weather,
        description="Get weather information for a specific city",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit",
                    "default": "celsius"
                }
            },
            "required": ["city"]
        }
    )
    print("Custom weather skill registered\n")
    
    print("Step 4: Listing all available skills:")
    for skill_name in agent.skills.keys():
        print(f"  - {skill_name}")
    print()
    
    print("Step 5: Example conversations:\n")
    
    examples = [
        "What's 125 divided by 5?",
        "What time is it now?",
        "Search for the word 'Python' in this text: 'I love Python programming'",
    ]
    
    for example in examples:
        print(f"User: {example}")
        print("Agent: Processing with OpenAI API format...")
        print("Note: Set OPENAI_API_KEY in .env to enable actual LLM responses")
        print()
    
    print("=" * 50)
    print("Example complete!")
    print("=" * 50)
    print()
    print("To run with a real OpenAI API:")
    print("1. Copy .env.example to .env")
    print("2. Add your OPENAI_API_KEY")
    print("3. Run: python example_usage.py")
    print()
    print("To start the API server:")
    print("1. Configure .env file")
    print("2. Run: python server.py")
    print("3. Visit: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
