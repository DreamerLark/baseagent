import asyncio
from agent import BaseAgent
from skills import SkillCategory


async def main():
    print("=== BaseAgent Usage Example ===\n")
    
    agent = BaseAgent()
    
    print("Step 1: Listing default skills...")
    skills = await agent.list_all_skills()
    print(f"Available skills: {list(skills['skills'].keys())}")
    print()
    
    print("Step 2: Testing skill execution...")
    result = await agent.skill_registry.execute("calculate", operation="add", a=15, b=27)
    if result.success:
        print(f"Calculate 15 + 27 = {result.data['result']}")
    else:
        print(f"Error: {result.error}")
    print()
    
    print("Step 3: Adding a custom weather skill...")
    def get_weather(city: str, unit: str = "celsius") -> dict:
        return {
            "city": city,
            "temperature": 22,
            "unit": unit,
            "condition": "Sunny",
            "humidity": 65,
            "wind_speed": 10
        }
    
    await agent.register_skill(
        name="get_weather",
        version="1.0.0",
        description="Get weather information for a specific city",
        func=get_weather,
        input_schema={
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
        },
        output_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "temperature": {"type": "number"},
                "unit": {"type": "string"},
                "condition": {"type": "string"},
                "humidity": {"type": "number"},
                "wind_speed": {"type": "number"}
            }
        },
        category=SkillCategory.CUSTOM,
        tags=["weather", "forecast"]
    )
    print("Weather skill registered\n")
    
    print("Step 4: Testing custom skill...")
    result = await agent.skill_registry.execute("get_weather", city="Beijing")
    if result.success:
        print(f"Weather in Beijing: {result.data}")
    else:
        print(f"Error: {result.error}")
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
    
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
