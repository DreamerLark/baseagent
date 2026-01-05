import os
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories following AgentSkills specification"""
    CREATIVE = "creative"
    DEVELOPMENT = "development"
    ENTERPRISE = "enterprise"
    DOCUMENT = "document"
    UTILITIES = "utilities"
    CUSTOM = "custom"


@dataclass
class SkillFrontmatter:
    """YAML frontmatter for skills following Anthropic Skills spec"""
    name: str
    description: str
    version: Optional[str] = "1.0.0"
    category: Optional[SkillCategory] = SkillCategory.CUSTOM
    tags: Optional[List[str]] = field(default_factory=list)
    examples: Optional[List[str]] = field(default_factory=list)
    guidelines: Optional[List[str]] = field(default_factory=list)
    instructions: Optional[str] = None


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
    Individual skill implementation following Anthropic Skills specification
    Based on SKILL.md with YAML frontmatter and markdown instructions
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        instructions: str,
        version: str = "1.0.0",
        category: SkillCategory = SkillCategory.CUSTOM,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        guidelines: Optional[List[str]] = None,
        resources: Optional[Dict[str, str]] = None
    ):
        self.frontmatter = SkillFrontmatter(
            name=name,
            description=description,
            instructions=instructions,
            version=version,
            category=category,
            tags=tags or [],
            examples=examples or [],
            guidelines=guidelines or []
        )
        self.resources = resources or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary representation"""
        return {
            "name": self.frontmatter.name,
            "description": self.frontmatter.description,
            "version": self.frontmatter.version,
            "category": self.frontmatter.category,
            "tags": self.frontmatter.tags,
            "examples": self.frontmatter.examples,
            "guidelines": self.frontmatter.guidelines,
            "instructions": self.frontmatter.instructions,
            "resources": self.resources
        }
        
    def to_markdown(self) -> str:
        """Convert skill to markdown format"""
        frontmatter_dict = asdict(self.frontmatter)
        frontmatter_yaml = yaml.dump(frontmatter_dict, default_flow_style=False, allow_unicode=True)
        
        markdown_content = "---\n"
        markdown_content += frontmatter_yaml
        markdown_content += "---\n\n"
        
        if self.frontmatter.instructions:
            markdown_content += self.frontmatter.instructions
        
        if self.frontmatter.examples:
            markdown_content += "\n\n## Examples\n"
            for example in self.frontmatter.examples:
                markdown_content += f"- {example}\n"
        
        if self.frontmatter.guidelines:
            markdown_content += "\n\n## Guidelines\n"
            for guideline in self.frontmatter.guidelines:
                markdown_content += f"- {guideline}\n"
        
        return markdown_content
        
    def to_openai_tool_definition(self) -> Dict[str, Any]:
        """Convert skill to OpenAI function calling format for compatibility"""
        return {
            "type": "function",
            "function": {
                "name": self.frontmatter.name,
                "description": self.frontmatter.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True
                }
            }
        }


class SkillRegistry:
    """
    Registry for skills following Anthropic Skills specification
    https://github.com/anthropics/skills
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._register_default_skills()
        
    def _register_default_skills(self):
        """Register built-in skills following Anthropic Skills spec"""
        
        # Current time skill
        self.register_skill(
            name="current-time",
            description="Get the current date and time in the specified timezone",
            instructions="""You are a time assistant. When asked for the current time, provide the current date and time clearly and accurately.

When responding to time requests:
- Always specify the timezone
- Use ISO 8601 format for dates and 24-hour format for times
- If no timezone is specified, use the local timezone
- Be clear about whether it's morning/afternoon/evening

Example responses:
- "The current time is 2024-01-15 14:30:25 UTC"
- "Today is January 15, 2024 at 2:30 PM PST"
""",
            category=SkillCategory.UTILITIES,
            tags=["time", "datetime", "current"],
            examples=[
                "What time is it?",
                "What's the current date and time in Tokyo?",
                "What timezone are you using?"
            ],
            guidelines=[
                "Always include timezone information",
                "Use clear, human-readable formats",
                "Be precise with time zones"
            ]
        )
        
        # Calculator skill
        self.register_skill(
            name="calculator",
            description="Perform arithmetic calculations including addition, subtraction, multiplication, division, and more",
            instructions="""You are a calculator assistant. Perform accurate mathematical calculations and provide clear, step-by-step explanations when helpful.

For calculations:
- Show your work for complex problems
- Round results to appropriate precision
- Check for edge cases (division by zero, negative numbers, etc.)
- Use standard mathematical notation

Supported operations:
- Basic arithmetic: +, -, *, /
- Advanced: power (^), square root (√)
- Order of operations applies

Example responses:
- "2 + 3 = 5"
- "For 15% of 80: 0.15 × 80 = 12"
""",
            category=SkillCategory.UTILITIES,
            tags=["math", "calculator", "arithmetic"],
            examples=[
                "What's 15% of 80?",
                "Calculate 2^10",
                "What is the square root of 144?"
            ],
            guidelines=[
                "Show work for complex calculations",
                "Use appropriate precision",
                "Check for edge cases"
            ]
        )
        
        # File operations skill
        self.register_skill(
            name="file-operations",
            description="Read and write files, including text files, configuration files, and documents",
            instructions="""You are a file operations assistant. Help users read, write, and manage files safely and efficiently.

For file operations:
- Always verify file paths and permissions
- Handle different text encodings (UTF-8, ASCII, etc.)
- Provide file size and modification information
- Be careful with file permissions and security
- Use appropriate file extensions

File operations available:
- Read text files
- Write text files
- Create backup copies when overwriting
- Validate file formats and encoding

Example responses:
- "Successfully read file.txt (1,234 bytes)"
- "Created new file data.json with 567 bytes"
- "File already exists - created backup copy"
""",
            category=SkillCategory.UTILITIES,
            tags=["file", "io", "read", "write"],
            examples=[
                "Read the contents of config.json",
                "Write a summary to report.txt",
                "Create a backup of data.csv"
            ],
            guidelines=[
                "Always verify file paths",
                "Handle encoding properly",
                "Create backups when overwriting"
            ]
        )
        
        # Text processing skill
        self.register_skill(
            name="text-processing",
            description="Search, analyze, and manipulate text content including finding patterns and extracting information",
            instructions="""You are a text processing assistant. Help users search, analyze, and manipulate text content effectively.

For text operations:
- Support case-sensitive and case-insensitive searches
- Provide context around found text
- Count occurrences and provide statistics
- Extract patterns and structured information
- Handle various text formats and encodings

Available operations:
- Find text patterns and keywords
- Extract specific information
- Count words, lines, characters
- Format and transform text
- Compare text versions

Example responses:
- "Found 'error' in 3 locations in log.txt"
- "Extracted 5 email addresses from the text"
- "The text contains 1,247 words in 23 paragraphs"
""",
            category=SkillCategory.UTILITIES,
            tags=["text", "search", "analysis", "extract"],
            examples=[
                "Find all occurrences of 'TODO' in the code",
                "Extract email addresses from this text",
                "Count the number of lines in the file"
            ],
            guidelines=[
                "Provide context for found text",
                "Use appropriate search methods",
                "Handle different text encodings"
            ]
        )
        
    def register_skill(
        self,
        name: str,
        description: str,
        instructions: str,
        version: str = "1.0.0",
        category: SkillCategory = SkillCategory.CUSTOM,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        guidelines: Optional[List[str]] = None,
        resources: Optional[Dict[str, str]] = None
    ):
        """
        Register a new skill following Anthropic Skills specification
        
        Args:
            name: Unique skill name (lowercase, hyphens for spaces)
            description: Human-readable description of what the skill does
            instructions: Detailed instructions for how the skill should behave
            version: Skill version (semver)
            category: Skill category
            tags: List of tags for organization
            examples: Example usage patterns
            guidelines: Guidelines for using the skill
            resources: Additional resources or files
        """
        skill = Skill(
            name=name,
            description=description,
            instructions=instructions,
            version=version,
            category=category,
            tags=tags or [],
            examples=examples or [],
            guidelines=guidelines or [],
            resources=resources
        )
        self.skills[name] = skill
        
    def load_skill_from_markdown(self, markdown_content: str, resources: Optional[Dict[str, str]] = None):
        """Load a skill from markdown content"""
        if markdown_content.startswith('---'):
            # Split frontmatter and content
            parts = markdown_content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_yaml = parts[1].strip()
                instructions = parts[2].strip()
            else:
                raise ValueError("Invalid markdown format")
            
            # Parse YAML frontmatter
            try:
                frontmatter_data = yaml.safe_load(frontmatter_yaml)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML frontmatter: {e}")
            
            # Validate required fields
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in frontmatter_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse category if present
            category = SkillCategory.CUSTOM
            if 'category' in frontmatter_data:
                try:
                    category = SkillCategory(frontmatter_data['category'])
                except ValueError:
                    category = SkillCategory.CUSTOM
            
            # Create skill
            self.register_skill(
                name=frontmatter_data['name'],
                description=frontmatter_data['description'],
                instructions=instructions or frontmatter_data.get('instructions', ''),
                version=frontmatter_data.get('version', '1.0.0'),
                category=category,
                tags=frontmatter_data.get('tags', []),
                examples=frontmatter_data.get('examples', []),
                guidelines=frontmatter_data.get('guidelines', []),
                resources=resources
            )
        else:
            raise ValueError("Markdown must start with YAML frontmatter")
        
    def load_skill_from_file(self, filepath: str):
        """Load a skill from a markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Check for additional resources in the same directory
            skill_dir = os.path.dirname(filepath) if os.path.dirname(filepath) else "."
            skill_name = os.path.basename(filepath).replace('.md', '')
            resources = {}
            
            # Look for resource files
            for filename in os.listdir(skill_dir):
                if filename.startswith(skill_name + '_') and filename != 'SKILL.md':
                    resource_path = os.path.join(skill_dir, filename)
                    try:
                        with open(resource_path, 'r', encoding='utf-8') as rf:
                            resources[filename] = rf.read()
                    except Exception:
                        continue  # Skip files that can't be read
            
            self.load_skill_from_markdown(markdown_content, resources)
        except FileNotFoundError:
            raise ValueError(f"Skill file not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Error loading skill from file: {e}")
        
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
            if skill.frontmatter.category == category
        ]
        
    def get_skills_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all skills with a specific tag"""
        return [
            skill.to_dict()
            for skill in self.skills.values()
            if tag in skill.frontmatter.tags
        ]
        
    def to_markdown_files(self, output_dir: str):
        """Export all skills to markdown files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for skill in self.skills.values():
            filename = f"{skill.frontmatter.name}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(skill.to_markdown())
        
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Convert all skills to OpenAI function calling format for compatibility"""
        return [skill.to_openai_tool_definition() for skill in self.skills.values()]
