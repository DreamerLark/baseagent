import json
from typing import Dict, Any, List, Optional
import httpx


class MCPClient:
    def __init__(self, server_url: str, timeout: int = 30):
        self.server_url = server_url
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout)
        
    def list_tools(self) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(f"{self.server_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.session.post(
                f"{self.server_url}/tools/{tool_name}",
                json={"arguments": arguments}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"MCP tool call failed: {str(e)}"}
    
    def list_resources(self) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(f"{self.server_url}/resources")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing resources: {e}")
            return []
    
    def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        try:
            response = self.session.get(
                f"{self.server_url}/resources",
                params={"uri": resource_uri}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Resource read failed: {str(e)}"}
    
    def close(self):
        self.session.close()


class MCPManager:
    def __init__(self):
        self.servers: Dict[str, MCPClient] = {}
    
    def add_server(self, name: str, server_url: str, timeout: int = 30):
        client = MCPClient(server_url, timeout)
        self.servers[name] = client
        return client
    
    def get_server(self, name: str) -> Optional[MCPClient]:
        return self.servers.get(name)
    
    def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        all_tools = {}
        for server_name, client in self.servers.items():
            all_tools[server_name] = client.list_tools()
        return all_tools
    
    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if server_name not in self.servers:
            return {"error": f"Server '{server_name}' not found"}
        
        client = self.servers[server_name]
        return client.call_tool(tool_name, arguments)
    
    def close_all(self):
        for client in self.servers.values():
            client.close()
