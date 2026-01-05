#!/usr/bin/env python3
"""
Example usage of BaseAgent with MCP integration
"""

import asyncio
from agent import BaseAgent
from skills import SkillCategory


async def main():
    print("=== BaseAgent with MCP Integration Example ===\n")
    
    agent = BaseAgent()
    
    print("Step 1: Listing default skills...")
    skills = await agent.list_all_skills()
    print(f"Available skills: {list(skills['skills'].keys())}")
    print()
    
    print("Step 2: Setting up MCP servers...")
    print("Note: MCP servers use stdio communication and JSON-RPC 2.0")
    print("Example MCP server commands:")
    print("  - ['python', 'mcp_server.py']")
    print("  - ['npx', '-y', '@modelcontextprotocol/server-filesystem', '/path/to/dir']")
    print()
    print("To add an MCP server, use:")
    print("  await agent.register_mcp_server('server_name', ['command', 'args'])")
    print()
    
    print("Step 3: Adding a custom weather skill...")
    await agent.register_skill(
        name="get-weather",
        description="Get weather information for a specific city",
        instructions="""You are a weather information assistant. Provide accurate and helpful weather information.

For weather requests:
- Always specify the temperature unit (Celsius or Fahrenheit)
- Include humidity and wind speed when available
- Provide weather condition descriptions
- Be clear about the data source and time
- Use friendly, conversational language

Available information:
- Current temperature
- Weather conditions (sunny, cloudy, rainy, etc.)
- Humidity percentage
- Wind speed and direction
- Forecast for the next few hours/days

Example responses:
- "The current weather in Beijing is 22°C, sunny with 65% humidity"
- "It's partly cloudy in London at 18°C, with a light breeze"
- "Tokyo is experiencing light rain at 20°C"
""",
        category=SkillCategory.UTILITIES,
        tags=["weather", "forecast", "climate"],
        examples=[
            "What's the weather like in Tokyo?",
            "Get weather for New York in Fahrenheit",
            "Is it raining in London?"
        ],
        guidelines=[
            "Always include temperature units",
            "Provide context for weather conditions",
            "Be conversational and friendly"
        ]
    )
    print("Weather skill registered\n")
    
    print("Step 4: Testing skill execution...")
    
    # Test the weather skill (simulated response)
    print("Testing weather skill...")
    weather_info = {
        "skill_name": "get-weather",
        "description": "Get weather information for a specific city",
        "instructions": "You are a weather information assistant...",
        "category": "utilities",
        "tags": ["weather", "forecast", "climate"],
        "message": "Skill 'get-weather' is now active. Follow the instructions provided."
    }
    print(f"Weather skill activated: {weather_info['message']}")
    print()
    
    print("Step 5: MCP Tools would be available here...")
    print("Note: MCP servers need to be configured separately")
    print("Example MCP tools might include:")
    print("  - filesystem_read, filesystem_write")
    print("  - database_query, database_update")
    print("  - api_call, web_search")
    print()
    
    print("Step 6: Example conversations:")
    examples = [
        "What's the weather in Beijing?",
        "Check if it's raining in London",
        "Get the temperature in Tokyo in Fahrenheit",
    ]
    
    for example in examples:
        print(f"User: {example}")
        print("Agent: [Skill would be activated based on context]")
        print()
    
    print("=" * 60)
    print("Example complete!")
    print("=" * 60)
    print()
    print("To use with real MCP servers:")
    print("1. Install MCP servers: npm install -g @modelcontextprotocol/server-filesystem")
    print("2. Add an MCP server: await agent.register_mcp_server('filesystem', ['npx', '-y', '@modelcontextprotocol/server-filesystem', '/path/to/dir'])")
    print("3. Chat with the agent to use both skills and MCP tools")
    print()
    print("To run with a real OpenAI API:")
    print("1. Copy .env.example to .env")
    print("2. Add your OPENAI_API_KEY")
    print("3. Run: python example_mcp.py")
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())