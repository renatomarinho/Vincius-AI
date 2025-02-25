from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Core.logger_base import LoggerBase

class APIMethod(ABC):
    """Base class for API methods"""
    
    def __init__(self, logger: LoggerBase):
        self.fs_manager = FileSystemManager()
        self.logger = logger
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get HTTP method name"""
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
