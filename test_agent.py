import asyncio
import unittest
from agent import BaseAgent
from skills import SkillCategory, SkillRegistry


class TestSkillRegistry(unittest.TestCase):
    """Test the SkillRegistry implementation following AgentSkills specification"""
    
    def setUp(self):
        self.registry = SkillRegistry()
        
    def test_default_skills_registered(self):
        """Test that default skills are registered"""
        skills = self.registry.get_all_skills()
        self.assertIn("calculate", skills)
        self.assertIn("get_current_time", skills)
        self.assertIn("read_file", skills)
        self.assertIn("write_file", skills)
        self.assertIn("search_text", skills)
        
    def test_skill_execution(self):
        """Test skill execution"""
        async def run_test():
            result = await self.registry.execute("calculate", operation="add", a=5, b=3)
            self.assertTrue(result.success)
            self.assertEqual(result.data["result"], 8)
            
        asyncio.run(run_test())
        
    def test_skill_error_handling(self):
        """Test skill error handling"""
        async def run_test():
            result = await self.registry.execute("nonexistent_skill")
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
            
        asyncio.run(run_test())
        
    def test_custom_skill_registration(self):
        """Test registering a custom skill"""
        def custom_function(x: int) -> dict:
            return {"result": x * 2}
            
        self.registry.register_skill(
            name="double",
            version="1.0.0",
            description="Double a number",
            func=custom_function,
            input_schema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer"}
                },
                "required": ["x"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "integer"}
                }
            },
            category=SkillCategory.MATH,
            tags=["math", "multiplication"]
        )
        
        async def run_test():
            result = await self.registry.execute("double", x=21)
            self.assertTrue(result.success)
            self.assertEqual(result.data["result"], 42)
            
        asyncio.run(run_test())
        
    def test_skill_manifest(self):
        """Test skill manifest structure"""
        skill = self.registry.get_skill("calculate")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.manifest.name, "calculate")
        self.assertEqual(skill.manifest.version, "1.0.0")
        self.assertEqual(skill.manifest.category, SkillCategory.MATH)
        self.assertIn("math", skill.manifest.tags)
        
    def test_skill_to_openai_format(self):
        """Test conversion to OpenAI function calling format"""
        openai_tools = self.registry.to_openai_tools()
        self.assertTrue(len(openai_tools) > 0)
        
        calculate_tool = next((t for t in openai_tools if t["function"]["name"] == "calculate"), None)
        self.assertIsNotNone(calculate_tool)
        self.assertEqual(calculate_tool["type"], "function")
        self.assertIn("parameters", calculate_tool["function"])


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
        def custom_func(value: str) -> dict:
            return {"result": value.upper()}
            
        async def run_test():
            await self.agent.register_skill(
                name="uppercase",
                version="1.0.0",
                description="Convert string to uppercase",
                func=custom_func,
                input_schema={
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"}
                    },
                    "required": ["value"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "string"}
                    }
                },
                category=SkillCategory.TEXT_PROCESSING
            )
            
            result = await self.agent.skill_registry.execute("uppercase", value="hello")
            self.assertTrue(result.success)
            self.assertEqual(result.data["result"], "HELLO")
            
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
    print("Running BaseAgent Tests")
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
