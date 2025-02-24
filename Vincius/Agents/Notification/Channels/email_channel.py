from typing import Dict, Any, Union
from pathlib import Path
from Vincius.Agents.Notification.Channels.base_channel import NotificationChannel

class EmailChannel(NotificationChannel):
    def get_channel_name(self) -> str:
        return "email"  # Must match exactly with workflow.yaml config

    def format_notification(self, content: Union[str, Dict]) -> Dict[str, Any]:
        message_text = self._ensure_string_content(content)

        return {
            "path": f"{self.docs_path}/email_notification.html",
            "type": "html",
            "content": f"""<!DOCTYPE html>
<html>
<head><title>Email Notification</title></head>
<body>
{message_text}
</body>
</html>""",
            "description": "Email notification"
        }

    def get_channel_rules(self) -> Dict[str, Any]:
        return {
            "name": "email",
            "max_length": None,
            "supports_html": True,
            "format_rules": [
                "Must have subject (max 60 chars)",
                "HTML formatting allowed",
                "Professional signature required"
            ],
            "structure": {
                "subject": "Required",
                "body": "HTML",
                "signature": "Required"
            }
        }
