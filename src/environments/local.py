import os
import subprocess
from dataclasses import dataclass, field

@dataclass
class LocalEnvironmentConfig:
    cwd: str = ""
    env: dict[str, str] = field(default_factory=dict)
    timeout: int = 30

class LocalEnvironment:
    def __init__(self, config: LocalEnvironmentConfig = LocalEnvironmentConfig()):
        self.config = config

    def execute(self, command: str):
        """执行命令并返回结果"""
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            cwd=self.config.cwd or os.getcwd(),
            env=os.environ | self.config.env,
            timeout=self.config.timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return {"output": result.stdout, "returncode": result.returncode}