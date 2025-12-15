import asyncio
import sys
from pathlib import Path
from typing import List

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from src.tools.mcp_utils import MCPTool
from src.tools.protocol import Tool, ToolSet


class MathToolSet(ToolSet):
    """Toolset for mathematical calculations."""

    def __init__(self):
        self._toolset_dir = Path(__file__).resolve().parent
        self._load_metadata()
        self._tools: List[Tool] = []  # Tools are loaded dynamically

    def _load_metadata(self):
        self._name = "math"
        self._description = "Performs basic arithmetic. Supports addition, subtraction, multiplication, and factorials. Does NOT support division."
        self._keywords = ["math", "calculate", "add", "subtract", "multiply", "factorial", "计算", "加", "减", "乘", "阶乘"]

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
        if not self._tools:
            self._tools = self._load_mcp_tools()
        return self._tools

    def _load_mcp_tools(self) -> List[Tool]:
        server_script = self._toolset_dir / "server.py"
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_script)],
            env=None
        )

        async def _fetch_tools():
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    return [
                        MCPTool(t.name, t.description, t.inputSchema, server_params)
                        for t in tools_result.tools
                    ]
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(_fetch_tools())


