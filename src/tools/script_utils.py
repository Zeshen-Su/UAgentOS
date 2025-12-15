import subprocess
import sys
from typing import Any, Dict, List
import json
from src.tools.protocol import Tool


class CodeTool(Tool):
    """ 以Code的形式进行TOOL的执行 """

    def __init__(self, name: str, description: str, script_path: str, parameters: Dict[str, Any]):
        self._name = name
        self._description = description
        self._script_path = script_path
        self._parameters = parameters

    @property
    def name(self) -> str:
        return self._name

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self._description,
            "parameters": self._parameters,
        }

    def execute(self, **kwargs) -> str:
        input_json = json.dumps(kwargs, ensure_ascii=False)
        
        try:
            result = subprocess.run(
                [sys.executable, self._script_path, input_json],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error executing script: {e.stderr}"
        except Exception as e:
            return f"Unexpected error: {e}"
