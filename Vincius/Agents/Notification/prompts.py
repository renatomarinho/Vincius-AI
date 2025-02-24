from typing import Dict, Any

class NotificationPrompts:
    @staticmethod
    def create_notification(data: str, channel_name: str, channel_rules: Dict[str, Any]) -> str:
        return f"""
Create a notification message for the {channel_name} channel based on this data:

{data}

Channel Rules and Requirements:
{channel_rules}

Format your response following these exact rules:

FILE: notifications/{channel_name}_notification.txt
Type: text
Description: Notification content for {channel_name}
Content:
[Your notification content here following the channel's rules and format]

Requirements:
1. Follow ALL channel-specific rules
2. Use appropriate formatting for {channel_name}
3. Keep content clear and professional
4. Include all critical information
5. Follow length and structure requirements
"""
