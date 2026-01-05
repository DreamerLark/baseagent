import json
import asyncio
import subprocess
import sys
from typing import Dict, Any, List, Optional, AnyStr
from dataclasses import dataclass, field


@dataclass
class MCPCapabilities:
    """MCP Server capabilities"""
    tools: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    prompts: Dict[str, Any] = field(default_factory=dict)


class MCPClient:
    """
    MCP Client following Model Context Protocol specification
    https://modelcontextprotocol.io/docs/getting-started/intro
    
    MCP uses JSON-RPC 2.0 over stdio for communication
    """
    
    def __init__(self, command: List[str], timeout: int = 30, env: Optional[Dict[str, str]] = None):
        """
        Initialize MCP client with server command
        
        Args:
            command: Command to start the MCP server (e.g., ["python", "server.py"])
            timeout: Default timeout for requests
            env: Environment variables for the subprocess (optional)
        """
        self.command = command
        self.timeout = timeout
        self.env = env
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.capabilities: Optional[MCPCapabilities] = None
        self.initialized = False
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Start the MCP server process"""
        # Prepare environment variables
        env = None
        if self.env:
            env = os.environ.copy()
            env.update(self.env)
        
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            env=env
        )
        
        # Initialize the connection
        await self._initialize()
        
    async def _initialize(self):
        """Perform MCP initialization handshake"""
        init_result = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "baseagent-mcp-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        await self._send_notification("notifications/initialized")
        
        self.initialized = True
        self.capabilities = MCPCapabilities(**init_result.get("capabilities", {}))
        
    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
        
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a JSON-RPC 2.0 request
        
        Args:
            method: The JSON-RPC method name
            params: The method parameters
            
        Returns:
            The JSON-RPC response result
        """
        if not self.process:
            raise RuntimeError("MCP client not started")
            
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
            
        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # Read response
        response_str = self.process.stdout.readline()
        
        if not response_str:
            raise RuntimeError("No response from MCP server")
            
        try:
            response = json.loads(response_str.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {e}")
            
        # Check for JSON-RPC errors
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"MCP error: {error.get('message', 'Unknown error')} (code: {error.get('code')})")
            
        return response.get("result", {})
        
    async def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """
        Send a JSON-RPC 2.0 notification (no response expected)
        
        Args:
            method: The JSON-RPC method name
            params: The method parameters
        """
        if not self.process:
            raise RuntimeError("MCP client not started")
            
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params:
            notification["params"] = params
            
        notification_str = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_str)
        self.process.stdin.flush()
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server
        
        Returns:
            List of tool definitions
        """
        result = await self._send_request("tools/list")
        return result.get("tools", [])
        
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a tool on the MCP server
        
        Args:
            name: The tool name
            arguments: The tool arguments
            
        Returns:
            The tool execution result
        """
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        return result
        
    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from the MCP server
        
        Returns:
            List of resource definitions
        """
        result = await self._send_request("resources/list")
        return result.get("resources", [])
        
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource from the MCP server
        
        Args:
            uri: The resource URI
            
        Returns:
            The resource content
        """
        result = await self._send_request("resources/read", {
            "uri": uri
        })
        return result
        
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List available prompts from the MCP server
        
        Returns:
            List of prompt definitions
        """
        result = await self._send_request("prompts/list")
        return result.get("prompts", [])
        
    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get a prompt from the MCP server
        
        Args:
            name: The prompt name
            arguments: The prompt arguments
            
        Returns:
            The prompt content
        """
        result = await self._send_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })
        return result
        
    async def close(self):
        """Close the MCP client connection"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
        self.initialized = False


class MCPManager:
    """Manager for multiple MCP servers"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        
    async def add_server(self, name: str, command: List[str], timeout: int = 30, env: Optional[Dict[str, str]] = None) -> MCPClient:
        """
        Add an MCP server
        
        Args:
            name: Server name
            command: Command to start the server
            timeout: Request timeout
            env: Environment variables for the subprocess (optional)
            
        Returns:
            The MCP client instance
        """
        client = MCPClient(command, timeout, env)
        await client.start()
        self.clients[name] = client
        return client
        
    def get_server(self, name: str) -> Optional[MCPClient]:
        """Get an MCP server by name"""
        return self.clients.get(name)
        
    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List tools from all connected servers"""
        all_tools = {}
        for server_name, client in self.clients.items():
            tools = await client.list_tools()
            all_tools[server_name] = tools
        return all_tools
        
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on a specific server"""
        if server_name not in self.clients:
            return {"error": f"Server '{server_name}' not found"}
            
        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)
        
    async def close_all(self):
        """Close all MCP server connections"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()
