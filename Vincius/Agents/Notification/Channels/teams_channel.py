from typing import Dict, Any, Union
from Vincius.Agents.Notification.Channels.base_channel import NotificationChannel

class TeamsChannel(NotificationChannel):
    def get_channel_name(self) -> str:
        return "teams"

    def format_notification(self, content: Union[str, Dict]) -> Dict[str, Any]:
        message_text = self._ensure_string_content(content)
        
        return {
            "path": f"{self.docs_path}/teams_notification.md",
            "type": "markdown",
            "content": message_text,
            "description": "Teams notification"
        }

    def get_channel_rules(self) -> Dict[str, Any]:
        return {
            "name": "teams",
            "max_length": 4000,
            "format_rules": [
                "Adaptive cards supported",
                "Rich formatting allowed",
                "Can use @mentions"
            ],
            "structure": {
                "title": "Required",
                "message": "Required",
                "actions": "Optional"
            }
        }
