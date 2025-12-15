import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Memory:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.user_preferences: List[str] = []  
        
        # 创建一个字典来进行记忆存储
        self.memory_data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.memory_data_dir, exist_ok=True)

    def add_message(self, role: str, content: str):
        """ 在对话历史中更新消息 """
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def clear_history(self):
        """ 清空消息 """
        self.history = []

    def add_preference(self, preference: str):
        """ 可记录用户偏好 """
        self.user_preferences.append(preference)
        

    def get_context(self) -> str:
        """
        把历史记录化为字符串以适应于LLM的上下文形式
        """
        context_str = ""
        for msg in self.history:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            context_str += f"{role}: {content}\n"
        return context_str

    def save_conversation(self, filename: str = "chat_log.txt"):
        """ 存储记录 """
        filepath = os.path.join(self.memory_data_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.get_context())
            return filepath
        except Exception as e:
            print(f"Failed to save conversation: {e}")
            return None

# Global memory instance
memory = Memory()
