import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories following AgentSkills specification"""
    UTILITIES = "utilities"
    MATH = "math"
    FILE_OPERATIONS = "file_operations"
    TEXT_PROCESSING = "text_processing"
    DATA_MANIPULATION = "data_manipulation"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    CUSTOM = "custom"


@dataclass
class SkillManifest:
    """
    Skill manifest following AgentSkills specification
    https://agentskills.io/home
    """
    name: str
    version: str
    description: str
    author: str = "baseagent"
    category: SkillCategory = SkillCategory.CUSTOM
    tags: List[str] = field(default_factory=list)
    license: str = "MIT"
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    
    # Input/output schemas following JSON Schema
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SkillExecutionResult:
    """Result of skill execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Skill:
    """
    Individual skill implementation following AgentSkills specification
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        func: Callable,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        author: str = "baseagent",
        category: SkillCategory = SkillCategory.CUSTOM,
        tags: Optional[List[str]] = None,
        documentation: Optional[str] = None
    ):
        self.manifest = SkillManifest(
            name=name,
            version=version,
            description=description,
            author=author,
            category=category,
            tags=tags or [],
            documentation=documentation,
            input_schema=input_schema,
            output_schema=output_schema
        )
        self.func = func
        
    async def execute(self, **kwargs) -> SkillExecutionResult:
        """Execute the skill with given arguments"""
        import time
        start_time = time.time()
        
        try:
            result = self.func(**kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            return SkillExecutionResult(
                success=True,
                data=result,
                execution_time_ms=execution_time,
                metadata={"version": self.manifest.version}
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return SkillExecutionResult(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary representation"""
        return {
            "manifest": asdict(self.manifest),
            "name": self.manifest.name
        }
        
    def to_openai_tool_definition(self) -> Dict[str, Any]:
        """Convert skill to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.manifest.name,
                "description": self.manifest.description,
                "parameters": self.manifest.input_schema
            }
        }


class SkillRegistry:
    """
    Registry for skills following AgentSkills specification
    https://agentskills.io/home
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._register_default_skills()
        
    def _register_default_skills(self):
        """Register built-in default skills"""
        
        # Get current time skill
        self.register_skill(
            name="get_current_time",
            version="1.0.0",
            description="Get the current date and time in the specified timezone",
            func=self._get_current_time,
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (optional, defaults to local)",
                        "default": "local"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "datetime": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "timezone": {"type": "string"}
                }
            },
            category=SkillCategory.UTILITIES,
            tags=["time", "datetime"]
        )
        
        # Calculate skill
        self.register_skill(
            name="calculate",
            version="1.0.0",
            description="Perform arithmetic calculations including add, subtract, multiply, divide, power, and sqrt",
            func=self._calculate,
            input_schema={
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
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"}
                }
            },
            category=SkillCategory.MATH,
            tags=["math", "calculator"]
        )
        
        # Read file skill
        self.register_skill(
            name="read_file",
            version="1.0.0",
            description="Read contents from a file at the specified path",
            func=self._read_file,
            input_schema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["filepath"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"},
                    "size": {"type": "integer"}
                }
            },
            category=SkillCategory.FILE_OPERATIONS,
            tags=["file", "read", "io"]
        )
        
        # Write file skill
        self.register_skill(
            name="write_file",
            version="1.0.0",
            description="Write content to a file at the specified path",
            func=self._write_file,
            input_schema={
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
            },
            output_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "status": {"type": "string"},
                    "bytes_written": {"type": "integer"}
                }
            },
            category=SkillCategory.FILE_OPERATIONS,
            tags=["file", "write", "io"]
        )
        
        # Search text skill
        self.register_skill(
            name="search_text",
            version="1.0.0",
            description="Search for occurrences of a query string within a given text",
            func=self._search_text,
            input_schema={
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
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "found": {"type": "boolean"},
                    "count": {"type": "integer"},
                    "occurrences": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "line": {"type": "integer"},
                                "index": {"type": "integer"},
                                "context": {"type": "string"}
                            }
                        }
                    }
                }
            },
            category=SkillCategory.TEXT_PROCESSING,
            tags=["search", "text", "find"]
        )
        
    def register_skill(
        self,
        name: str,
        version: str,
        description: str,
        func: Callable,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        author: str = "baseagent",
        category: SkillCategory = SkillCategory.CUSTOM,
        tags: Optional[List[str]] = None,
        documentation: Optional[str] = None
    ):
        """
        Register a new skill
        
        Args:
            name: Unique skill name
            version: Skill version (semver)
            description: Human-readable description
            func: Function to execute the skill
            input_schema: JSON Schema for input validation
            output_schema: JSON Schema for output structure
            author: Skill author
            category: Skill category
            tags: List of tags for organization
            documentation: Optional documentation URL or text
        """
        skill = Skill(
            name=name,
            version=version,
            description=description,
            func=func,
            input_schema=input_schema,
            output_schema=output_schema,
            author=author,
            category=category,
            tags=tags or [],
            documentation=documentation
        )
        self.skills[name] = skill
        
    async def execute(self, skill_name: str, **kwargs) -> SkillExecutionResult:
        """
        Execute a skill by name
        
        Args:
            skill_name: Name of the skill to execute
            **kwargs: Arguments to pass to the skill
            
        Returns:
            SkillExecutionResult containing the execution result
        """
        if skill_name not in self.skills:
            return SkillExecutionResult(
                success=False,
                error=f"Skill '{skill_name}' not found in registry"
            )
            
        skill = self.skills[skill_name]
        return await skill.execute(**kwargs)
        
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(skill_name)
        
    def get_all_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get all skills as dictionaries"""
        return {
            name: skill.to_dict()
            for name, skill in self.skills.items()
        }
        
    def get_skills_by_category(self, category: SkillCategory) -> List[Dict[str, Any]]:
        """Get all skills in a specific category"""
        return [
            skill.to_dict()
            for skill in self.skills.values()
            if skill.manifest.category == category
        ]
        
    def get_skills_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all skills with a specific tag"""
        return [
            skill.to_dict()
            for skill in self.skills.values()
            if tag in skill.manifest.tags
        ]
        
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert all skills to OpenAI function calling format"""
        return [skill.to_openai_tool_definition() for skill in self.skills.values()]
        
    # Static skill implementations
    
    @staticmethod
    def _get_current_time(timezone: str = "local") -> Dict[str, Any]:
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": timezone
        }
        
    @staticmethod
    def _calculate(operation: str, a: float, b: float = None) -> Dict[str, Any]:
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
    def _read_file(filepath: str) -> Dict[str, Any]:
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
    def _write_file(filepath: str, content: str) -> Dict[str, Any]:
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
    def _search_text(text: str, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
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
