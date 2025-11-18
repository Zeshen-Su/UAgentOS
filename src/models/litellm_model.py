import litellm

class LitellmModel:
    def __init__(self, api_key: str, model_name: str, api_base: str = None, custom_llm_provider: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.api_base = api_base
        self.custom_llm_provider = custom_llm_provider

    def generate_response(self, task: str, template: str) -> str:
        messages = [
            {"role": "system", "content": template},
            {"role": "user", "content": task},
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