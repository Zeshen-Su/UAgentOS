import json
import os
import yaml
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from src.tools.registry import registry, ToolSetSummary
from src.models.litellm_model import LitellmModel
from src.memory.core import memory  
load_dotenv()


BRAIN_PROVIDER = os.getenv("BRAIN_PROVIDER", "default-provider")
BRAIN_MODEL_NAME = os.getenv("BRAIN_MODEL_NAME", "default-model")
BRAIN_API_KEY = os.getenv("BRAIN_API_KEY", "default-key")
BRAIN_API_URL = os.getenv("BRAIN_API_URL", "default-url")
BRAIN_CONFIGURED = os.getenv("BRAIN_CONFIGURED", "false").lower() == "true"


def _initialise_brain_model() -> Optional[LitellmModel]:
    if not BRAIN_CONFIGURED:
        return None
    return LitellmModel(
        api_key=BRAIN_API_KEY,
        model_name=BRAIN_MODEL_NAME,
        api_base=BRAIN_API_URL,
        custom_llm_provider=BRAIN_PROVIDER,
    )


brain_model = _initialise_brain_model()


def _load_system_prompt_template() -> str:
    config_path = os.path.join(os.path.dirname(__file__), "agent.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["brain"]["system_prompt_template"].strip()


SYSTEM_PROMPT_TEMPLATE = _load_system_prompt_template()


def _build_system_prompt() -> str:
    # 可使用memory获得格式化的历史记录
    history_str = memory.get_context()
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        toolsets=registry.formatted_summaries(),
        history=history_str
    )


def _fallback_response(user_request: str, reason: str) -> Dict[str, str]:
    match: Optional[ToolSetSummary] = registry.match_by_keyword(user_request)
    if match:
        code = f"print(run_toolset('{match.name}', '{user_request}'))"
        return {"type": "code", "content": code}
    
    return {"type": "question", "content": f"Brain fallback: {reason}. I'm not sure what to do. Can you clarify?"}


def get_brain_response(user_request: str) -> Dict[str, str]:
    if not user_request.strip():
        return {"type": "question", "content": "Please provide a request."}

    if brain_model is None:
        return _fallback_response(user_request, "Brain model not configured")

    print(f"Thinking with brain model ({BRAIN_MODEL_NAME})...")
    try:
        # 将最新的用户请求作为“任务”传递，提示中包含了内存中的完整历史记录
        system_prompt = _build_system_prompt()
        raw = brain_model.generate_response(user_request, system_prompt)
    except Exception as exc:
        return _fallback_response(user_request, f"Brain model failed: {exc}")

    # Parse JSON
    try:
        # 可清理markdown json块
        json_str = raw.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
        
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError:
        print(f"Failed to parse Brain JSON: {raw}")
        return _fallback_response(user_request, "Invalid JSON from Brain")


__all__ = ["get_brain_response"]
