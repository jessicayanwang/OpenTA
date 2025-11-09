"""
Base Tool Class
All tools inherit from this
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Abstract base class for all tools
    Tools are capabilities that agents can use
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Any:
        """
        Execute the tool with given parameters
        Must be implemented by each tool
        """
        pass
    
    def validate_params(self, params: Dict[str, Any], required_keys: list) -> bool:
        """Validate that required parameters are present"""
        return all(key in params for key in required_keys)
