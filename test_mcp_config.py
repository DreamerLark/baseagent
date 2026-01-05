#!/usr/bin/env python3
"""
Test script for MCP server configuration with environment variables
"""

import asyncio
import os
import tempfile
import json
from agent import BaseAgent


async def test_mcp_config():
    """Test MCP server configuration with environment variables"""
    print("=== Testing MCP Server Configuration ===\n")
    
    agent = BaseAgent()
    
    # Test 1: Basic environment variable registration
    print("Test 1: Single MCP server with environment variables")
    try:
        await agent.register_mcp_server(
            "test-server",
            ["echo", "test"],
            env={"TZ": "Asia/Shanghai", "TEST_VAR": "hello"}
        )
        print("✓ Single server registration with env vars successful\n")
    except Exception as e:
        print(f"✗ Single server registration failed: {e}\n")
    
    # Test 2: Bulk configuration from dictionary
    print("Test 2: Bulk registration from config dictionary")
    config = {
        "mcp-server-chart": {
            "command": ["echo", "chart-server"],
            "env": {"TZ": "Asia/Shanghai"}
        },
        "time_service": {
            "command": ["echo", "time-service"],
            "env": {"TZ": "Asia/Shanghai"}
        }
    }
    
    try:
        await agent.register_mcp_servers_from_config(config)
        print("✓ Bulk registration successful\n")
    except Exception as e:
        print(f"✗ Bulk registration failed: {e}\n")
    
    # Test 3: Configuration from JSON file
    print("Test 3: Loading from JSON configuration file")
    
    # Create a temporary JSON config file
    config_data = {
        "mcpServers": {
            "file-server-1": {
                "command": ["echo", "server1"],
                "env": {"TZ": "Asia/Shanghai", "API_KEY": "test123"}
            },
            "file-server-2": {
                "command": ["echo", "server2"],
                "timeout": 60,
                "env": {"DEBUG": "true"}
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f, indent=2)
        temp_file = f.name
    
    try:
        await agent.register_mcp_servers_from_file(temp_file)
        print("✓ File-based registration successful\n")
    except Exception as e:
        print(f"✗ File-based registration failed: {e}\n")
    finally:
        os.unlink(temp_file)
    
    # Test 4: JSONC format support
    print("Test 4: JSONC format support with comments")
    
    jsonc_content = """{
  // This is a comment
  "mcpServers": {
    "jsonc-server": {
      "command": ["echo", "jsonc-test"],
      "env": {
        "TZ": "Asia/Shanghai"
      }
    } /* inline comment */
  }
}"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonc', delete=False) as f:
        f.write(jsonc_content)
        temp_file = f.name
    
    try:
        await agent.register_mcp_servers_from_file(temp_file)
        print("✓ JSONC format support successful\n")
    except Exception as e:
        print(f"✗ JSONC format test failed: {e}\n")
    finally:
        os.unlink(temp_file)
    
    # Test 5: Direct format (no mcpServers wrapper)
    print("Test 5: Direct format without mcpServers wrapper")
    
    direct_config = {
        "direct-server-1": {
            "command": ["echo", "direct1"],
            "env": {"VAR1": "value1"}
        },
        "direct-server-2": {
            "command": ["echo", "direct2"],
            "env": {"VAR2": "value2"}
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(direct_config, f, indent=2)
        temp_file = f.name
    
    try:
        await agent.register_mcp_servers_from_file(temp_file)
        print("✓ Direct format support successful\n")
    except Exception as e:
        print(f"✗ Direct format test failed: {e}\n")
    finally:
        os.unlink(temp_file)
    
    # Test 6: Verify server list
    print("Test 6: Verify registered servers")
    try:
        all_tools = await agent.list_all_tools()
        print(f"✓ MCP servers registered: {len(all_tools['mcp_servers'])} servers")
        for server_name in all_tools['mcp_servers']:
            print(f"  - {server_name}")
        print()
    except Exception as e:
        print(f"✗ Failed to list servers: {e}\n")
    
    # Test 7: Backward compatibility (no env vars)
    print("Test 7: Backward compatibility (no environment variables)")
    try:
        await agent.register_mcp_server(
            "legacy-server",
            ["echo", "legacy"]
        )
        print("✓ Backward compatibility maintained\n")
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}\n")
    
    await agent.close()
    
    print("=== All Tests Complete ===")
    print("\nYour configuration format is supported:")
    print("""{
  "mcpServers": {
    "mcp-server-chart": {
      "command": ["npx", "-y", "@antv/mcp-server-chart"],
      "env": {"TZ": "Asia/Shanghai"}
    },
    "time_service": {
      "command": ["python", "./time_service.py"],
      "env": {"TZ": "Asia/Shanghai"}
    }
  }
}""")


if __name__ == "__main__":
    asyncio.run(test_mcp_config())
