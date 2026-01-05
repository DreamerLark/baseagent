#!/usr/bin/env python3
"""
简单的 MCP 服务器示例 - 时间服务
支持获取当前时间、格式化时间等操作
"""

import asyncio
import json
import time
from datetime import datetime
import sys


async def handle_request(request):
    """处理 MCP 请求"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            # 服务器初始化
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "time-service",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            # 列出可用工具
            tools = [
                {
                    "name": "get_current_time",
                    "description": "获取当前时间",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "description": "时间格式 (iso, timestamp, readable)",
                                "enum": ["iso", "timestamp", "readable"],
                                "default": "iso"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "时区 (例如: Asia/Shanghai, UTC)",
                                "default": "Asia/Shanghai"
                            }
                        }
                    }
                },
                {
                    "name": "format_timestamp",
                    "description": "格式化时间戳",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "timestamp": {
                                "type": "number",
                                "description": "Unix 时间戳"
                            },
                            "format": {
                                "type": "string",
                                "description": "输出格式",
                                "enum": ["iso", "readable", "date"],
                                "default": "readable"
                            }
                        },
                        "required": ["timestamp"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }
        
        elif method == "tools/call":
            # 调用工具
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_current_time":
                return await handle_get_current_time(arguments, request_id)
            
            elif tool_name == "format_timestamp":
                return await handle_format_timestamp(arguments, request_id)
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32600,
                "message": f"Internal error: {str(e)}"
            }
        }


async def handle_get_current_time(arguments, request_id):
    """处理获取当前时间的请求"""
    format_type = arguments.get("format", "iso")
    timezone = arguments.get("timezone", "Asia/Shanghai")
    
    try:
        # 设置时区
        import os
        os.environ["TZ"] = timezone
        time.tzset()  # 更新时区设置
        
        now = datetime.now()
        
        if format_type == "iso":
            result = now.isoformat()
        elif format_type == "timestamp":
            result = int(now.timestamp())
        elif format_type == "readable":
            result = now.strftime("%Y年%m月%d日 %H:%M:%S")
        else:
            result = now.isoformat()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "time": result,
                            "format": format_type,
                            "timezone": timezone,
                            "timestamp": now.timestamp()
                        }, ensure_ascii=False)
                    }
                ]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Error getting current time: {str(e)}"
            }
        }


async def handle_format_timestamp(arguments, request_id):
    """处理格式化时间戳的请求"""
    timestamp = arguments.get("timestamp")
    format_type = arguments.get("format", "readable")
    
    if timestamp is None:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "Missing required parameter: timestamp"
            }
        }
    
    try:
        dt = datetime.fromtimestamp(timestamp)
        
        if format_type == "iso":
            result = dt.isoformat()
        elif format_type == "readable":
            result = dt.strftime("%Y年%m月%d日 %H:%M:%S")
        elif format_type == "date":
            result = dt.strftime("%Y年%m月%d日")
        else:
            result = dt.isoformat()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "formatted_time": result,
                            "original_timestamp": timestamp,
                            "format": format_type
                        }, ensure_ascii=False)
                    }
                ]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Error formatting timestamp: {str(e)}"
            }
        }


async def main():
    """主函数 - 处理标准输入输出"""
    while True:
        try:
            # 读取请求
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
            
            # 解析 JSON-RPC 请求
            request = json.loads(line.strip())
            
            # 处理请求
            response = await handle_request(request)
            
            # 发送响应
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Server error: {str(e)}"
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())