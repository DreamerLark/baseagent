#!/usr/bin/env python3
"""
BaseAgent CLI - Command line interface for BaseAgent with skill and MCP support
"""

import asyncio
import json
import os
import click
from typing import Optional
from agent import BaseAgent


def get_agent(ctx):
    """Get or create BaseAgent instance from context"""
    if 'agent' not in ctx.obj:
        ctx.obj['agent'] = BaseAgent(
            api_key=ctx.obj.get('api_key'),
            base_url=ctx.obj.get('base_url'),
            model=ctx.obj.get('model')
        )
    return ctx.obj['agent']


@click.group()
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--base-url', envvar='OPENAI_BASE_URL', default='https://api.openai.com/v1', help='OpenAI base URL')
@click.option('--model', envvar='OPENAI_MODEL', default='gpt-4-turbo-preview', help='Model to use')
@click.pass_context
def cli(ctx, api_key, base_url, model):
    """BaseAgent CLI with skill and MCP support"""
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['base_url'] = base_url
    ctx.obj['model'] = model
    # agent will be created lazily in get_agent()


@cli.result_callback()
@click.pass_context
def process_result(ctx, result, **kwargs):
    """Cleanup after command execution"""
    if 'agent' in ctx.obj:
        try:
            asyncio.run(ctx.obj['agent'].close())
        except:
            pass


@cli.command()
@click.pass_context
def chat(ctx):
    """Start an interactive chat session"""
    agent = get_agent(ctx)
    
    if not agent.client:
        click.echo("Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
        return
    
    click.echo("=== BaseAgent Chat ===")
    click.echo("Type 'quit' or 'exit' to end the session")
    click.echo("Available features:")
    click.echo("- Skills: Built-in skills for various tasks")
    click.echo("- MCP Tools: External tools via MCP servers")
    click.echo("")
    
    try:
        while True:
            try:
                message = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                click.echo("\nGoodbye!")
                break
            
            if message.lower() in ['quit', 'exit']:
                click.echo("Goodbye!")
                break
            
            if not message:
                continue
            
            click.echo("Agent: ", nl=False)
            try:
                response = agent.chat_sync(message)
                click.echo(response)
            except Exception as e:
                click.echo(f"Error: {str(e)}")
            
            click.echo("")
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.pass_context
def list_skills(ctx):
    """List all available skills"""
    agent = get_agent(ctx)
    
    try:
        skills = asyncio.run(agent.list_all_skills())
        click.echo("=== Available Skills ===\n")
        
        for skill_name, skill_data in skills['skills'].items():
            click.echo(f"📚 {skill_name}")
            click.echo(f"   Description: {skill_data['description']}")
            click.echo(f"   Category: {skill_data.get('category', 'custom')}")
            if skill_data.get('tags'):
                click.echo(f"   Tags: {', '.join(skill_data['tags'])}")
            click.echo("")
        
        click.echo(f"Total: {len(skills['skills'])} skills")
    except Exception as e:
        click.echo(f"Error listing skills: {str(e)}")
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.pass_context
def list_mcp(ctx):
    """List all registered MCP servers and tools"""
    agent = get_agent(ctx)
    
    try:
        tools = asyncio.run(agent.list_all_tools())
        click.echo("=== MCP Servers ===\n")
        
        mcp_servers = tools.get('mcp_tools', {})
        if not mcp_servers:
            click.echo("No MCP servers registered.")
        else:
            for server_name, server_info in mcp_servers.items():
                click.echo(f"🔧 {server_name}")
                if isinstance(server_info, dict):
                    click.echo(f"   Command: {server_info.get('command', 'N/A')}")
                    click.echo(f"   Timeout: {server_info.get('timeout', 'N/A')}")
                    click.echo(f"   Initialized: {server_info.get('initialized', 'N/A')}")
                    if server_info.get('env'):
                        click.echo(f"   Environment: {len(server_info['env'])} variables")
                    tools_count = len(server_info.get('tools', []))
                    click.echo(f"   Tools: {tools_count} available")
                click.echo("")
        
        click.echo(f"Total: {len(mcp_servers)} MCP servers")
    except Exception as e:
        click.echo(f"Error listing MCP servers: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.argument('name')
@click.argument('description')
@click.argument('instructions', type=click.Path(exists=False))
@click.option('--version', default='1.0.0', help='Skill version')
@click.option('--category', default='custom', help='Skill category')
@click.option('--tags', multiple=True, help='Skill tags')
@click.pass_context
def add_skill(ctx, name, description, instructions, version, category, tags):
    """Add a new skill from a file"""
    agent = get_agent(ctx)
    
    try:
        # Read instructions from file
        with open(instructions, 'r', encoding='utf-8') as f:
            instructions_text = f.read()
        
        asyncio.run(agent.register_skill(
            name=name,
            description=description,
            instructions=instructions_text,
            version=version,
            category=category,
            tags=list(tags) if tags else None
        ))
        
        click.echo(f"✓ Skill '{name}' added successfully")
    except FileNotFoundError:
        click.echo(f"Error: Instructions file '{instructions}' not found")
    except Exception as e:
        click.echo(f"Error adding skill: {str(e)}")
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def load_mcp_config(ctx, config_file):
    """Load MCP servers from configuration file"""
    agent = get_agent(ctx)
    
    try:
        asyncio.run(agent.register_mcp_servers_from_file(config_file))
        click.echo(f"✓ MCP configuration loaded from {config_file}")
    except Exception as e:
        click.echo(f"Error loading MCP configuration: {str(e)}")
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.argument('name')
@click.argument('command', nargs=-1, required=True)
@click.option('--timeout', default=30, help='Request timeout in seconds')
@click.option('--env', multiple=True, help='Environment variables in KEY=VALUE format')
@click.pass_context
def add_mcp_server(ctx, name, command, timeout, env):
    """Add an MCP server"""
    agent = get_agent(ctx)
    
    try:
        # Parse environment variables
        env_dict = {}
        for env_var in env:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_dict[key] = value
        
        asyncio.run(agent.register_mcp_server(
            name=name,
            command=list(command),
            timeout=timeout,
            env=env_dict if env_dict else None
        ))
        
        click.echo(f"✓ MCP server '{name}' added successfully")
    except Exception as e:
        click.echo(f"Error adding MCP server: {str(e)}")
    finally:
        asyncio.run(agent.close())


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def generate_config(ctx, output):
    """Generate a sample MCP configuration file"""
    
    config = {
        "mcpServers": {
            "filesystem": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {
                    "TZ": "Asia/Shanghai"
                }
            },
            "weather": {
                "command": ["python", "./weather_service.py"],
                "timeout": 30,
                "env": {
                    "API_KEY": "your-api-key-here",
                    "TZ": "Asia/Shanghai"
                }
            },
            "calculator": {
                "command": ["node", "./calculator_server.js"],
                "env": {
                    "DEBUG": "true"
                }
            }
        }
    }
    
    if output:
        try:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            click.echo(f"✓ Sample configuration generated at {output}")
        except Exception as e:
            click.echo(f"Error writing configuration file: {str(e)}")
    else:
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))


@cli.command()
@click.pass_context
def info(ctx):
    """Show agent configuration and status"""
    agent = get_agent(ctx)
    
    click.echo("=== BaseAgent Information ===\n")
    click.echo(f"Model: {agent.model}")
    click.echo(f"API Base URL: {agent.base_url}")
    click.echo(f"API Key: {'✓ Configured' if agent.api_key else '✗ Not configured'}")
    click.echo(f"Client: {'✓ Initialized' if agent.client else '✗ Not initialized'}")
    click.echo("")
    
    # List skills
    try:
        skills = asyncio.run(agent.list_all_skills())
        click.echo(f"Skills: {len(skills['skills'])} registered")
    except:
        click.echo("Skills: Unable to retrieve")
    
    # List MCP servers
    try:
        tools = asyncio.run(agent.list_all_tools())
        mcp_count = len(tools.get('mcp_tools', {}))
        click.echo(f"MCP Servers: {mcp_count} registered")
    except:
        click.echo("MCP Servers: Unable to retrieve")
    
    click.echo("")
    click.echo("Environment variables:")
    click.echo("  OPENAI_API_KEY - OpenAI API key")
    click.echo("  OPENAI_BASE_URL - OpenAI base URL (default: https://api.openai.com/v1)")
    click.echo("  OPENAI_MODEL - Model to use (default: gpt-4-turbo-preview)")
    
    asyncio.run(agent.close())


@cli.command()
@click.pass_context
def examples(ctx):
    """Show usage examples"""
    click.echo("=== BaseAgent CLI Examples ===\n")
    
    click.echo("1. Start interactive chat:")
    click.echo("   python cli.py chat")
    click.echo("")
    
    click.echo("2. List all skills:")
    click.echo("   python cli.py list-skills")
    click.echo("")
    
    click.echo("3. List MCP servers:")
    click.echo("   python cli.py list-mcp")
    click.echo("")
    
    click.echo("4. Generate sample MCP configuration:")
    click.echo("   python cli.py generate-config --output mcp-config.json")
    click.echo("")
    
    click.echo("5. Load MCP configuration:")
    click.echo("   python cli.py load-mcp-config mcp-config.json")
    click.echo("")
    
    click.echo("6. Add MCP server manually:")
    click.echo("   python cli.py add-mcp-server filesystem npx -y @modelcontextprotocol/server-filesystem /tmp")
    click.echo("")
    
    click.echo("7. Add skill from file:")
    click.echo("   python cli.py add-skill calculator 'Perform calculations' instructions.md")
    click.echo("")
    
    click.echo("8. Show agent info:")
    click.echo("   python cli.py info")
    click.echo("")
    
    click.echo("Environment setup:")
    click.echo("   export OPENAI_API_KEY=your-api-key")
    click.echo("   export OPENAI_MODEL=gpt-4-turbo-preview")


if __name__ == '__main__':
    cli()