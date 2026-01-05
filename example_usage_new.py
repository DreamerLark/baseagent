#!/usr/bin/env python3
"""
Example usage of BaseAgent with Anthropic Skills specification
"""

import asyncio
from agent import BaseAgent
from skills import SkillCategory


async def main():
    """Demonstrate BaseAgent with Anthropic Skills"""
    
    # Initialize the agent
    agent = BaseAgent()
    
    # Register skills following Anthropic Skills specification
    print("🔧 Registering skills...")
    
    # Calculator skill
    await agent.register_skill(
        name="calculator",
        description="Perform arithmetic calculations including addition, subtraction, multiplication, division, and more",
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
        tags=["math", "calculator", "arithmetic"],
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
    
    # Text processor skill
    await agent.register_skill(
        name="text-processor",
        description="Search, analyze, and manipulate text content including finding patterns and extracting information",
        instructions="""You are a text processing assistant. Help users search, analyze, and manipulate text content effectively.

For text operations:
- Support case-sensitive and case-insensitive searches
- Provide context around found text
- Count occurrences and provide statistics
- Extract patterns and structured information
- Handle various text formats and encodings

Available operations:
- Find text patterns and keywords
- Extract specific information
- Count words, lines, characters
- Format and transform text
- Compare text versions

Example responses:
- "Found 'error' in 3 locations in log.txt"
- "Extracted 5 email addresses from the text"
- "The text contains 1,247 words in 23 paragraphs"
""",
        category=SkillCategory.UTILITIES,
        tags=["text", "search", "analysis", "extract"],
        examples=[
            "Find all occurrences of 'TODO' in the code",
            "Extract email addresses from this text",
            "Count the number of lines in the file"
        ],
        guidelines=[
            "Provide context for found text",
            "Use appropriate search methods",
            "Handle different text encodings"
        ]
    )
    
    # File operations skill
    await agent.register_skill(
        name="file-operations",
        description="Read and write files, including text files, configuration files, and documents",
        instructions="""You are a file operations assistant. Help users read, write, and manage files safely and efficiently.

For file operations:
- Always verify file paths and permissions
- Handle different text encodings (UTF-8, ASCII, etc.)
- Provide file size and modification information
- Be careful with file permissions and security
- Use appropriate file extensions

File operations available:
- Read text files
- Write text files
- Create backup copies when overwriting
- Validate file formats and encoding

Example responses:
- "Successfully read file.txt (1,234 bytes)"
- "Created new file data.json with 567 bytes"
- "File already exists - created backup copy"
""",
        category=SkillCategory.UTILITIES,
        tags=["file", "io", "read", "write"],
        examples=[
            "Read the contents of config.json",
            "Write a summary to report.txt",
            "Create a backup of data.csv"
        ],
        guidelines=[
            "Always verify file paths",
            "Handle encoding properly",
            "Create backups when overwriting"
        ]
    )
    
    print("✓ Skills registered successfully")
    
    # List all available skills
    print("\n📋 Available Skills:")
    skills_info = await agent.list_all_skills()
    
    for skill_name, skill_data in skills_info["skills"].items():
        print(f"\n🔧 {skill_name}")
        print(f"   Description: {skill_data['description']}")
        print(f"   Category: {skill_data['category']}")
        print(f"   Tags: {', '.join(skill_data['tags'])}")
        if skill_data.get('examples'):
            print(f"   Examples: {len(skill_data['examples'])} examples")
    
    print("\n" + "=" * 60)
    print("Interactive Chat (Type 'quit' to exit)")
    print("=" * 60)
    
    # Interactive chat
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\nAgent is thinking...")
            response = await agent.chat(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Clean up
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())