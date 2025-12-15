from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.tools.protocol import ToolSet


@dataclass(frozen=True)
class ToolSetSummary:
    """ 构成：Metadata about a toolset """

    name: str
    description: str
    keywords: List[str]
    module: str
    class_name: str


_TOOLSET_SPECS = ()


class ToolRegistry:
    """ 对服务进行注册 """

    def __init__(self) -> None:
        self._entries: List[ToolSetSummary] = self._load_entries()

    def _load_entries(self) -> List[ToolSetSummary]:
        entries: List[ToolSetSummary] = []
        toolsets_dir = Path(__file__).resolve().parent.parent.parent / "toolsets"
        
        # 扫描TOOL
        for tool_md in toolsets_dir.glob("*/TOOL.md"):
            try:
                content = tool_md.read_text(encoding="utf-8")
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        front_matter = yaml.safe_load(parts[1])
                        module_name = f"toolsets.{tool_md.parent.name}"
                        
                        entries.append(
                            ToolSetSummary(
                                name=front_matter.get("name", tool_md.parent.name),
                                description=front_matter.get("description", ""),
                                keywords=front_matter.get("keywords", []),
                                module=module_name,
                                class_name=front_matter.get("class_name", ""),
                            )
                        )
            except Exception as e:
                print(f"Warning: Could not load metadata from {tool_md}: {e}")
                
        return entries

    def summaries(self) -> List[ToolSetSummary]:
        return list(self._entries)

    def formatted_summaries(self) -> str:
        lines: List[str] = []
        for entry in self._entries:
            lines.append(f"- {entry.name}: {entry.description}")
        return "\n".join(lines)

    def create(self, name: str) -> Optional[ToolSet]:
        entry = self.resolve(name)
        if not entry:
            return None
        try:
            module = import_module(entry.module)
            toolset_class = getattr(module, entry.class_name)
            return toolset_class()
        except (ImportError, AttributeError):
            return None

    def resolve(self, name: str) -> Optional[ToolSetSummary]:
        for entry in self._entries:
            if entry.name.lower() == name.lower():
                return entry
        return None

    def match_by_keyword(self, text: str) -> Optional[ToolSetSummary]:
        lowered = text.lower()
        for entry in self._entries:
            if any(keyword in lowered for keyword in entry.keywords):
                return entry
        return None


registry = ToolRegistry()

__all__ = ["ToolRegistry", "ToolSetSummary", "registry"]
