from typing import Dict, Any, Union
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    """Base class for notification channels"""
    
    @property
    def docs_path(self) -> str:
        return "docs/notifications"
    
    def _ensure_string_content(self, content: Union[str, Dict]) -> str:
        """Convert content to string safely"""
        if isinstance(content, dict):
            return str(content.get('message', content))
        return str(content)
    
    @abstractmethod
    def format_notification(self, content: Union[str, Dict]) -> Dict[str, Any]:
        """Format notification content for specific channel"""
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """Get channel name for documentation"""
        pass

    @abstractmethod
    def get_channel_rules(self) -> Dict[str, Any]:
        """Get channel-specific formatting rules"""
        pass
