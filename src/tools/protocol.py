from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Tool(ABC):
    """ Tool抽象基类 """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """ 返回描述 """       
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass


class ToolSet(ABC):
    """ Toolset抽象基类 """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def keywords(self) -> List[str]:
        """ 辅助AI匹配 """
        pass

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """ 获取工具所对应的TOOL列表 """
        pass
