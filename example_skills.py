#!/usr/bin/env python3
"""
Example script showing how to load and use skills following Anthropic Skills specification
"""

import asyncio
import os
from agent import BaseAgent
from skills import SkillCategory, SkillRegistry


async def main():
    """Demonstrate loading skills from markdown files"""
    
    # Create skill registry
    registry = SkillRegistry()
    
    # Load skill from markdown file
    try:
        registry.load_skill_from_file("/home/engine/project/skills_examples/calculator_skill.md")
        print("✓ Loaded calculator skill from markdown file")
    except Exception as e:
        print(f"✗ Failed to load skill: {e}")
    
    # Register a custom skill
    registry.register_skill(
        name="text-analyzer",
        description="Analyze text content for patterns, word count, and structure",
        instructions="""You are a text analysis assistant. Help users analyze and understand text content.

For text analysis:
- Count words, characters, lines, and paragraphs
- Identify patterns and themes
- Extract key information
- Provide readability metrics
- Highlight important sections

Available operations:
- Word count and frequency analysis
- Sentence structure analysis
- Paragraph organization
- Pattern recognition
- Key phrase extraction

Example responses:
- "The text contains 1,247 words in 23 paragraphs"
- "Most frequent words: 'the' (45), 'and' (32), 'to' (28)"
- "Average sentence length: 15.3 words"
""",
        category=SkillCategory.UTILITIES,
        tags=["text", "analysis", "count"],
        examples=[
            "Count the words in this paragraph",
            "Find the most common words",
            "Analyze the text structure"
        ],
        guidelines=[
            "Provide accurate counts",
            "Identify patterns clearly",
            "Use visual formatting for results"
        ]
    )
    
    # Print all skills
    print("\n📋 Registered Skills:")
    print("-" * 40)
    
    for skill_name, skill_data in registry.get_all_skills().items():
        print(f"\n🔧 {skill_name}")
        print(f"   Description: {skill_data['description']}")
        print(f"   Category: {skill_data['category']}")
        print(f"   Tags: {', '.join(skill_data['tags'])}")
        print(f"   Examples: {len(skill_data.get('examples', []))} examples")
    
    # Create agent with the skills
    agent = BaseAgent()
    agent.skill_registry = registry
    
    print("\n🤖 Agent initialized with Anthropic Skills")
    print("\n💡 Example interactions:")
    print("   - 'Calculate 15% of 80'")
    print("   - 'What's 2^10?'")
    print("   - 'Analyze this text...'")
    
    # Show OpenAI tool format conversion
    openai_tools = registry.to_openai_tools()
    print(f"\n🔗 Converted to {len(openai_tools)} OpenAI function calling tools")
    
    # Show markdown export
    export_dir = "/home/engine/project/exported_skills"
    registry.to_markdown_files(export_dir)
    print(f"\n📁 Exported skills to: {export_dir}")
    
    # List exported files
    if os.path.exists(export_dir):
        exported_files = os.listdir(export_dir)
        for filename in exported_files:
            print(f"   - {filename}")


if __name__ == "__main__":
    print("=" * 60)
    print("Anthropic Skills Example")
    print("=" * 60)
    asyncio.run(main())
    print("\n" + "=" * 60)