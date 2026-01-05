import asyncio
import unittest
from agent import BaseAgent
from skills import SkillCategory, SkillRegistry


class TestSkillRegistry(unittest.TestCase):
    """Test the SkillRegistry implementation following Anthropic Skills specification"""
    
    def setUp(self):
        self.registry = SkillRegistry()
        
    def test_default_skills_registered(self):
        """Test that default skills are registered"""
        skills = self.registry.get_all_skills()
        self.assertIn("current-time", skills)
        self.assertIn("calculator", skills)
        self.assertIn("file-operations", skills)
        self.assertIn("text-processing", skills)
        
    def test_skill_structure(self):
        """Test skill structure following Anthropic Skills spec"""
        skill = self.registry.get_skill("calculator")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.frontmatter.name, "calculator")
        self.assertEqual(skill.frontmatter.version, "1.0.0")
        self.assertEqual(skill.frontmatter.category, SkillCategory.UTILITIES)
        self.assertIn("math", skill.frontmatter.tags)
        self.assertIsNotNone(skill.frontmatter.instructions)
        self.assertIn("arithmetic", skill.frontmatter.description.lower())
        
    def test_skill_markdown_generation(self):
        """Test markdown generation for skills"""
        skill = self.registry.get_skill("calculator")
        markdown = skill.to_markdown()
        
        self.assertTrue(markdown.startswith("---"))
        self.assertIn("name:", markdown)
        self.assertIn("calculator", markdown)
        self.assertIn("description:", markdown)
        
    def test_load_skill_from_markdown(self):
        """Test loading skill from markdown content"""
        markdown_content = """---
name: test-skill
description: Test skill for markdown loading
version: "1.0.0"
category: utilities
tags: ["test", "example"]
---

# Test Skill
This is a test skill for verification.
"""
        
        self.registry.load_skill_from_markdown(markdown_content)
        skill = self.registry.get_skill("test-skill")
        
        self.assertIsNotNone(skill)
        self.assertEqual(skill.frontmatter.name, "test-skill")
        self.assertEqual(skill.frontmatter.category, SkillCategory.UTILITIES)
        self.assertIn("test", skill.frontmatter.tags)
        
    def test_skill_registration(self):
        """Test manual skill registration"""
        self.registry.register_skill(
            name="custom-skill",
            description="Custom test skill",
            instructions="You are a custom skill assistant.",
            category=SkillCategory.CUSTOM,
            tags=["custom", "test"]
        )
        
        skill = self.registry.get_skill("custom-skill")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.frontmatter.name, "custom-skill")
        self.assertEqual(skill.frontmatter.category, SkillCategory.CUSTOM)
        
    def test_skill_to_openai_format(self):
        """Test conversion to OpenAI function calling format"""
        openai_tools = self.registry.to_openai_tools()
        self.assertTrue(len(openai_tools) > 0)
        
        calculator_tool = next((t for t in openai_tools if t["function"]["name"] == "calculator"), None)
        self.assertIsNotNone(calculator_tool)
        self.assertEqual(calculator_tool["type"], "function")
        self.assertIn("arithmetic", calculator_tool["function"]["description"].lower())


class TestBaseAgent(unittest.TestCase):
    """Test the BaseAgent implementation"""
    
    def setUp(self):
        self.agent = BaseAgent()
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent.skill_registry)
        self.assertIsNotNone(self.agent.mcp_manager)
        
    def test_list_skills(self):
        """Test listing skills"""
        async def run_test():
            skills_info = await self.agent.list_all_skills()
            self.assertIn("skills", skills_info)
            self.assertIn("mcp_servers", skills_info)
            self.assertTrue(len(skills_info["skills"]) > 0)
            
        asyncio.run(run_test())
        
    def test_skill_registration(self):
        """Test registering a skill through agent"""
        async def run_test():
            await self.agent.register_skill(
                name="test-uppercase",
                description="Convert string to uppercase",
                instructions="You are a text transformation assistant that converts text to uppercase.",
                category=SkillCategory.UTILITIES,
                tags=["text", "transform"],
                examples=["Convert 'hello' to uppercase"]
            )
            
            skill = self.agent.skill_registry.get_skill("test-uppercase")
            self.assertIsNotNone(skill)
            self.assertEqual(skill.frontmatter.name, "test-uppercase")
            self.assertIn("uppercase", skill.frontmatter.description.lower())
            
        asyncio.run(run_test())
        
    def test_conversation_management(self):
        """Test conversation history management"""
        self.agent.conversation_history.append({
            "role": "user",
            "content": "Hello"
        })
        
        history = self.agent.get_conversation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "Hello")
        
        self.agent.reset_conversation()
        history = self.agent.get_conversation_history()
        self.assertEqual(len(history), 0)


class TestMCPClient(unittest.IsolatedAsyncioTestCase):
    """Test MCP client implementation"""
    
    def test_mcp_manager_initialization(self):
        """Test MCP manager initialization"""
        from mcp_client import MCPManager
        manager = MCPManager()
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.clients), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSkillRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestBaseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPClient))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 50)
    print("Running BaseAgent Tests (Anthropic Skills)")
    print("=" * 50)
    print()
    
    success = run_tests()
    
    print()
    print("=" * 50)
    if success:
        print("All tests passed! ✓")
    else:
        print("Some tests failed! ✗")
    print("=" * 50)
