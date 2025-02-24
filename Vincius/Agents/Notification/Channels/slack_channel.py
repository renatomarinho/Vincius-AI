from typing import Dict, Any, Union
from Vincius.Agents.Notification.Channels.base_channel import NotificationChannel

class SlackChannel(NotificationChannel):
    def get_channel_name(self) -> str:
        return "slack"

    def format_notification(self, content: Union[str, Dict]) -> Dict[str, Any]:
        message_text = self._ensure_string_content(content)
        
        return {
            "path": f"{self.docs_path}/slack_notification.md",
            "type": "markdown",
            "content": message_text,
            "description": "Slack notification"
        }

    def get_channel_rules(self) -> Dict[str, Any]:
        return {
            "name": "slack",
            "max_length": 3000,
            "format_rules": [
                "Markdown supported",
                "Can use emojis",
                "Mention users with @"
            ],
            "structure": {
                "header": "Required",
                "message": "Required",
                "attachments": "Optional"
            }
        }
