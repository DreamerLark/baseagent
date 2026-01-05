import os
import sys
from unittest.mock import Mock, patch
from agent import BaseAgent
from skills import SkillRegistry


def test_skill_registry():
    print("Testing SkillRegistry...")
    registry = SkillRegistry()
    
    skills = registry.get_all_skills()
    assert "calculate" in skills
    assert "get_current_time" in skills
    assert "read_file" in skills
    assert "write_file" in skills
    assert "search_text" in skills
    print("✓ SkillRegistry has all default skills")
    
    result = registry.execute("calculate", operation="add", a=5, b=3)
    assert result["result"] == 8
    print("✓ Calculate skill works: 5 + 3 = 8")
    
    result = registry.execute("calculate", operation="multiply", a=7, b=6)
    assert result["result"] == 42
    print("✓ Calculate skill works: 7 * 6 = 42")
    
    result = registry.execute("get_current_time")
    assert "datetime" in result
    assert "date" in result
    assert "time" in result
    print("✓ Get current time skill works")
    
    result = registry.execute("search_text", text="Hello World", query="World")
    assert result["found"] == True
    assert result["count"] == 1
    print("✓ Search text skill works")
    
    print("SkillRegistry tests passed!\n")


def test_agent_basic():
    print("Testing BaseAgent basic functionality...")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        agent = BaseAgent()
        
        assert agent.model is not None
        assert agent.skills is not None
        print("✓ Agent initialization works")
        
        def dummy_func(x: int, y: int):
            return {"result": x + y}
        
        agent.register_skill(
            name="test_skill",
            func=dummy_func,
            description="Test skill",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"}
                },
                "required": ["x", "y"]
            }
        )
        
        assert "test_skill" in agent.skills
        print("✓ Skill registration works")
        
        result = agent._execute_skill("test_skill", {"x": 10, "y": 20})
        assert result["result"] == 30
        print("✓ Skill execution works")
        
        tools = agent._convert_skills_to_tools()
        assert len(tools) > 0
        assert tools[0]["type"] == "function"
        print("✓ Skills to tools conversion works")
        
        agent.conversation_history.append({"role": "user", "content": "Hello"})
        history = agent.get_conversation_history()
        assert len(history) == 1
        print("✓ Conversation history works")
        
        agent.reset_conversation()
        assert len(agent.conversation_history) == 0
        print("✓ Conversation reset works")
    
    print("BaseAgent tests passed!\n")


def test_mcp_manager():
    print("Testing MCP functionality...")
    from mcp_client import MCPManager
    
    manager = MCPManager()
    assert len(manager.servers) == 0
    print("✓ MCPManager initialization works")
    
    print("MCPManager tests passed!\n")


def main():
    print("=" * 50)
    print("Running BaseAgent Tests")
    print("=" * 50)
    print()
    
    try:
        test_skill_registry()
        test_agent_basic()
        test_mcp_manager()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
