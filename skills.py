import os
import json
from datetime import datetime
from typing import Dict, Any, List


class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}
        self._register_default_skills()
    
    def _register_default_skills(self):
        self.register(
            name="get_current_time",
            func=self.get_current_time,
            description="Get the current date and time",
            parameters={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (optional, defaults to local)",
                        "default": "local"
                    }
                }
            }
        )
        
        self.register(
            name="calculate",
            func=self.calculate,
            description="Perform arithmetic calculations",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "The second number (not required for sqrt)"
                    }
                },
                "required": ["operation", "a"]
            }
        )
        
        self.register(
            name="read_file",
            func=self.read_file,
            description="Read contents from a file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["filepath"]
            }
        )
        
        self.register(
            name="write_file",
            func=self.write_file,
            description="Write contents to a file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filepath", "content"]
            }
        )
        
        self.register(
            name="search_text",
            func=self.search_text,
            description="Search for text in a given content",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to search in"
                    },
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search should be case-sensitive",
                        "default": False
                    }
                },
                "required": ["text", "query"]
            }
        )
    
    def register(self, name: str, func: callable, description: str, parameters: Dict[str, Any]):
        self.skills[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
    
    def execute(self, skill_name: str, **kwargs) -> Any:
        if skill_name not in self.skills:
            return {"error": f"Skill '{skill_name}' not found"}
        
        try:
            skill_func = self.skills[skill_name]["function"]
            result = skill_func(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Error executing skill '{skill_name}': {str(e)}"}
    
    def get_all_skills(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "description": skill["description"],
                "parameters": skill["parameters"]
            }
            for name, skill in self.skills.items()
        }
    
    @staticmethod
    def get_current_time(timezone: str = "local") -> Dict[str, Any]:
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": timezone
        }
    
    @staticmethod
    def calculate(operation: str, a: float, b: float = None) -> Dict[str, Any]:
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return {"error": "Division by zero"}
                result = a / b
            elif operation == "power":
                result = a ** b
            elif operation == "sqrt":
                result = a ** 0.5
            else:
                return {"error": f"Unknown operation: {operation}"}
            
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def read_file(filepath: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filepath}"}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "filepath": filepath,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def write_file(filepath: str, content: str) -> Dict[str, Any]:
        try:
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "filepath": filepath,
                "status": "success",
                "bytes_written": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def search_text(text: str, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        try:
            search_text = text if case_sensitive else text.lower()
            search_query = query if case_sensitive else query.lower()
            
            occurrences = []
            start = 0
            
            while True:
                index = search_text.find(search_query, start)
                if index == -1:
                    break
                
                line_start = text.rfind('\n', 0, index) + 1
                line_end = text.find('\n', index)
                if line_end == -1:
                    line_end = len(text)
                
                line = text[line_start:line_end]
                line_num = text[:index].count('\n') + 1
                
                occurrences.append({
                    "line": line_num,
                    "index": index,
                    "context": line
                })
                
                start = index + 1
            
            return {
                "query": query,
                "found": len(occurrences) > 0,
                "count": len(occurrences),
                "occurrences": occurrences
            }
        except Exception as e:
            return {"error": str(e)}
