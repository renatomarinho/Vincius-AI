from typing import Dict, Any, Union
from Vincius.Agents.Notification.Channels.base_channel import NotificationChannel

class WhatsappChannel(NotificationChannel):
    def get_channel_name(self) -> str:
        return "whatsapp"

    def format_notification(self, content: Union[str, Dict]) -> Dict[str, Any]:
        message_text = self._ensure_string_content(content)
        
        return {
            "path": f"{self.docs_path}/whatsapp_notification.txt",
            "type": "text",
            "content": message_text,
            "description": "WhatsApp notification"
        }

    def get_channel_rules(self) -> Dict[str, Any]:
        return {
            "name": "whatsapp",
            "max_length": 1000,
            "supports_markdown": False,
            "format_rules": [
                "Message must be concise and direct",
                "Can include emojis",
                "Can include one URL",
                "Can use basic formatting (bold, italic)",
                "Must follow WhatsApp Business API guidelines"
            ],
            "structure": {
                "header": "Optional, max 60 chars",
                "message": "Required, max 1000 chars",
                "footer": "Optional, max 60 chars",
                "buttons": "Optional, max 3 buttons"
            }
        }
