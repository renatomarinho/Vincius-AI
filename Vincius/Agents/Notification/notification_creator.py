from typing import Dict, Any, List, Union
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager
from Core.content_parser import ContentParser
from Vincius.Agents.Notification.Channels.base_channel import NotificationChannel
from Vincius.Agents.Notification.prompts import NotificationPrompts

class NotificationCreator:
    def __init__(self):
        self.fs_manager = FileSystemManager()
        self.content_parser = ContentParser()

    def create_notification(self, data: str, brain: Any, config: Dict, channels: List[NotificationChannel]) -> List[Path]:
        """Create notifications for each channel"""
        created_files = []
        
        try:
            for channel in channels:
                try:
                    print(f"\n📝 Generating content for {channel.get_channel_name()} channel...")
                    rules = channel.get_channel_rules()
                    
                    # Generate notification content
                    prompt = NotificationPrompts.create_notification(
                        data=data,
                        channel_name=channel.get_channel_name(),
                        channel_rules=rules
                    )
                    
                    response = brain.generate(prompt, config)
                    if not response:
                        print(f"❌ Failed to generate content for {channel.get_channel_name()}")
                        continue

                    # Extract and clean content
                    content = self._extract_content(response)
                    if content is None:
                        print(f"❌ Invalid content format for {channel.get_channel_name()}")
                        continue

                    # Format and save notification
                    try:
                        file_info = channel.format_notification(content)
                        if path := self.fs_manager.create_or_update_file(file_info):
                            created_files.append(path)
                            print(f"✅ Created notification for {channel.get_channel_name()}: {path}")
                    except Exception as format_error:
                        print(f"❌ Error formatting notification: {format_error}")
                        continue
                    
                except Exception as e:
                    print(f"❌ Error processing channel {channel.get_channel_name()}: {e}")
                    continue

            return created_files
            
        except Exception as e:
            print(f"❌ Error creating notifications: {e}")
            return []

    def _extract_content(self, response: Any) -> Union[str, Dict, None]:
        """Extract and clean content from model response"""
        try:
            # If response is already a dict, extract message or return full dict
            if isinstance(response, dict):
                return response.get('message', response)

            # If response is string
            if isinstance(response, str):
                # Try to find content section
                if 'Content:' in response:
                    content = response.split('Content:', 1)[1].strip()
                else:
                    content = response.strip()

                # Try to parse as JSON if it looks like a JSON string
                if content.startswith('{') and content.endswith('}'):
                    try:
                        import json
                        return json.loads(content)
                    except json.JSONDecodeError:
                        pass

                # Return as string if not JSON
                return content

            print(f"⚠️ Unexpected response type: {type(response)}")
            return str(response)

        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            return str(response)  # Return as string as fallback
