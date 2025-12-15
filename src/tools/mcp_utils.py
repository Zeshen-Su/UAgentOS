import asyncio
import sys
from typing import Any, Dict, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.tools.protocol import Tool


class MCPTool(Tool):
    """ 以MCP的形式进行TOOL的执行 """

    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], server_params: StdioServerParameters):
        self._name = name
        self._description = description
        self._input_schema = input_schema
        self._server_params = server_params

    @property
    def name(self) -> str:
        return self._name

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self._description,
            "parameters": self._input_schema,
        }

    def execute(self, **kwargs) -> str:
        async def _run():
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(self.name, arguments=kwargs)
                    return result

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(_run())
            
            text_content = []
            for item in result.content:
                if hasattr(item, 'text'):
                    text_content.append(item.text)
                else:
                    text_content.append(str(item))
            return ", ".join(text_content)
        except Exception as e:
            return f"Error executing MCP tool {self.name}: {e}"


