from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager

class APIMethod(ABC):
    """Base class for API methods"""
    
    def __init__(self):
        self.fs_manager = FileSystemManager()
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get HTTP method name"""
        pass
    
    @abstractmethod
    def get_method_prompt(self, input_data: Any, api_config: Dict) -> str:
        """Get method-specific prompt for request generation"""
        pass
    
    @abstractmethod
    def format_request(self, data: Any) -> Dict[str, Any]:
        """Format request data for this method"""
        pass
    
    @abstractmethod
    def get_method_rules(self) -> Dict[str, Any]:
        """Get method-specific rules and requirements"""
        pass
    
    def save_request(self, request: Dict[str, Any], input_data: Any) -> None:
        """Save the formatted request to a JSON file"""
        try:
            file_info = {
                "path": f"Docs/requests/{self.get_method_name().lower()}_request.json",
                "type": "json",
                "content": {
                    "method": self.get_method_name(),
                    "request": request,
                    "original_input": input_data
                },
                "description": f"{self.get_method_name()} request configuration"
            }
            
            if path := self.fs_manager.create_or_update_file(file_info):
                print(f"✅ Saved request configuration: {path}")
                
        except Exception as e:
            print(f"❌ Error saving request: {e}")

    def _ensure_valid_data(self, data: Any) -> Dict[str, Any]:
        """Ensure data is in correct format"""
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            try:
                import json
                return json.loads(data)
            except:
                return {"data": data}
        return {"data": str(data)}
