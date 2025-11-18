#!/usr/bin/env python3

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from src.models.litellm_model import LitellmModel
import subprocess
from brain import get_task_from_brain

load_dotenv()

# 定义用户请求
user_request = "这个人好搞笑啊，对吗"

# 获取 mini-agent 配置
CONFIG_PATH = Path(__file__).parent / "agent.yaml"
with CONFIG_PATH.open() as f:
    CONFIG = yaml.safe_load(f)

MINI_PROVIDER = os.getenv("MINI_PROVIDER", "default-provider")
MINI_MODEL_NAME = os.getenv("MINI_MODEL_NAME", "default-model")
MINI_API_KEY = os.getenv("MINI_API_KEY", "default-key")
MINI_API_URL = os.getenv("MINI_API_URL", "default-url")
MINI_CONFIGURED = os.getenv("MINI_CONFIGURED", "false").lower() == "true"

if not MINI_CONFIGURED:
    raise ValueError("Mini-agent model is not configured. Please check your .env file.")

model = LitellmModel(
    api_key=MINI_API_KEY,
    model_name=MINI_MODEL_NAME,
    api_base=MINI_API_URL,
    custom_llm_provider=MINI_PROVIDER
)

def main():
    task_sentence = get_task_from_brain(user_request)
    response = model.generate_response(task_sentence, CONFIG["agent"]["system_template"])

    if "```bash" in response:
        command = response.split("```bash\n")[1].split("\n```")[0]
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")

if __name__ == "__main__":
    main()