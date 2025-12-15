import json
from pathlib import Path
from typing import Any, Dict, List

from src.tools.protocol import Tool, ToolSet
from src.tools.script_utils import CodeTool


class PptxToolSet(ToolSet):
    """Toolset for creating PowerPoint presentations."""

    def __init__(self):
        self._toolset_dir = Path(__file__).resolve().parent
        self._load_metadata()
        
        # Load guidelines to enhance the tool description
        guidelines_path = self._toolset_dir / "outline_guidelines.md"
        guidelines = ""
        if guidelines_path.exists():
            guidelines = f"\n\nGuidelines:\n{guidelines_path.read_text(encoding='utf-8')}"

        self._tools = [
            CodeTool(
                name="generate_pptx_file",
                description=f"Generates a .pptx file from a structured JSON outline of slides. IMPORTANT: The input 'slides' must be a JSON array where each object has 'title' and 'bullet_points'. If the user provides raw text content, YOU (the LLM) MUST parse it into this JSON structure before calling this tool.{guidelines}",
                script_path=str(self._toolset_dir / "scripts" / "generate_pptx.py"),
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The main title of the presentation.",
                        },
                        "slides": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "bullet_points": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["title", "bullet_points"],
                            },
                            "description": "A list of slide objects, each with a title and bullet points.",
                        },
                    },
                    "required": ["title", "slides"],
                }
            )
        ]

    def _load_metadata(self):
        # This would typically parse TOOL.md front matter
        self._name = "pptx"
        self._description = "Generates PowerPoint presentations from a topic by first creating an outline and then building the .pptx file."
        self._keywords = ["ppt", "pptx", "presentation", "powerpoint", "slide", "演示", "汇报"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def keywords(self) -> List[str]:
        return self._keywords

    def get_tools(self) -> List[Tool]:
        return self._tools

