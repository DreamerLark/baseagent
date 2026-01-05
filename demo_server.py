#!/usr/bin/env python3
import json
import sys

def handle_request(request):
    request_id = request.get("id")
    method = request.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "demo", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "hello",
                        "description": "Say hello",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method {method} not found"}
        }

if __name__ == "__main__":
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except:
            break
