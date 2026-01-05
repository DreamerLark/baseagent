from agent import BaseAgent
from skills import SkillRegistry
from mcp_client import MCPManager


def main():
    print("=== BaseAgent Example Usage ===\n")
    
    agent = BaseAgent()
    skill_registry = SkillRegistry()
    
    for skill_name, skill_info in skill_registry.get_all_skills().items():
        agent.register_skill(
            name=skill_name,
            func=lambda sn=skill_name, **kwargs: skill_registry.execute(sn, **kwargs),
            description=skill_info["description"],
            parameters=skill_info["parameters"]
        )
    
    print("Registered skills:")
    for skill_name in skill_registry.get_all_skills().keys():
        print(f"  - {skill_name}")
    print()
    
    examples = [
        "What is the current time?",
        "Calculate 15 multiplied by 8",
        "What is 100 divided by 4?",
    ]
    
    print("Running example queries:\n")
    
    for example in examples:
        print(f"User: {example}")
        response = agent.chat(example)
        print(f"Agent: {response}")
        print()
    
    print("\n=== Interactive Mode ===")
    print("Type your questions (or 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
