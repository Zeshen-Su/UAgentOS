from __future__ import annotations

import litellm


_SURROGATE_FILTER = dict.fromkeys(range(0xD800, 0xE000), "")


class LitellmModel:
    def __init__(self, api_key: str, model_name: str, api_base: str = None, custom_llm_provider: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.api_base = api_base
        self.custom_llm_provider = custom_llm_provider

    @staticmethod
    def _sanitize(text: str) -> str:
        if not text:
            return ""
        return text.translate(_SURROGATE_FILTER)

    def generate_response(self, task: str, template: str) -> str:
        system_prompt = self._sanitize(template)
        user_prompt = self._sanitize(task)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        completion_kwargs = {
            "model": self.model_name,
            "messages": messages,
            "api_key": self.api_key,
        }
        if self.api_base:
            completion_kwargs["api_base"] = self.api_base
        if self.custom_llm_provider:
            completion_kwargs["custom_llm_provider"] = self.custom_llm_provider
            
        response = litellm.completion(**completion_kwargs)
        return response["choices"][0]["message"]["content"].strip()