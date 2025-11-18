import os
from src.models.litellm_model import LitellmModel
from dotenv import load_dotenv
import yaml
from pathlib import Path

load_dotenv()

# 建构 "大脑" 模型
BRAIN_PROVIDER = os.getenv("BRAIN_PROVIDER", "default-provider")
BRAIN_MODEL_NAME = os.getenv("BRAIN_MODEL_NAME", "default-model")
BRAIN_API_KEY = os.getenv("BRAIN_API_KEY", "default-key")
BRAIN_API_URL = os.getenv("BRAIN_API_URL", "default-url")
BRAIN_CONFIGURED = os.getenv("BRAIN_CONFIGURED", "false").lower() == "true"

if not BRAIN_CONFIGURED:
    raise ValueError("Brain model is not configured. Please check your .env file.")

brain_model = LitellmModel(
    api_key=BRAIN_API_KEY,
    model_name=BRAIN_MODEL_NAME,
    api_base=BRAIN_API_URL,
    custom_llm_provider=BRAIN_PROVIDER
)

CONFIG_PATH = Path(__file__).parent / "agent.yaml"
with CONFIG_PATH.open() as f:
    CONFIG = yaml.safe_load(f)

SYSTEM_PROMPT = CONFIG["brain"]["system_prompt"]

def get_task_from_brain(user_request: str) -> str:
    print(f"Thinking with brain model ({BRAIN_MODEL_NAME})...")
    task_sentence = brain_model.generate_response(user_request, SYSTEM_PROMPT)
    print(f"Brain response: {task_sentence}")
    return task_sentence.strip()
