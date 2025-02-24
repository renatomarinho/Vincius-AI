from typing import Dict, Any, List
from pathlib import Path
from Vincius.Core.brain_model import BrainModel
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.Notification.notification_creator import NotificationCreator
from Vincius.Agents.Notification.Channels import available_channels, NotificationChannel

class NotificationAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.brain = BrainModel()
        self.notification_creator = NotificationCreator()
        
        print("\n🔍 Initializing NotificationAgent...")
        
        # Initialize requested channels from config
        self.channels = []
        
        # Get channels directly from config since it's already flattened
        channel_configs = config.get('channels', [])
        
        print(f"\n📋 Channel Configuration:")
        print(f"- Channel configs found: {channel_configs}")
        print(f"- Available channels: {[c().get_channel_name() for c in available_channels]}")
        
        # Create instances of available channels that match config
        for channel_class in available_channels:
            try:
                channel = channel_class()
                channel_name = channel.get_channel_name()
                print(f"\nProcessing channel: {channel_name}")
                print(f"Looking for match in: {channel_configs}")
                
                if channel_name in channel_configs:
                    print(f"✅ Loading channel: {channel_name}")
                    self.channels.append(channel)
                else:
                    print(f"⚠️ Channel not configured: {channel_name}")
                    
            except Exception as e:
                print(f"❌ Error loading channel {channel_class.__name__}: {e}")

        print(f"\n📊 Channel Loading Summary:")
        print(f"- Total channels available: {len(available_channels)}")
        print(f"- Channels configured: {len(channel_configs)}")
        print(f"- Channels loaded: {len(self.channels)}")
        if self.channels:
            print(f"- Active channels: {[c.get_channel_name() for c in self.channels]}")
        else:
            print("⚠️ No channels were loaded!")

    def execute(self, input_data: Any = None) -> Any:
        try:
            print("\n📢 Starting notification generation...")
            
            if not input_data:
                return "Error: No notification data provided"

            if not self.channels:
                return "Error: No notification channels configured"

            # Create notifications for all channels
            created_files = self.notification_creator.create_notification(
                str(input_data),
                self.brain,
                self.config,
                self.channels
            )
            
            if not created_files:
                return "Error: Failed to create notifications"

            print(f"✅ Created {len(created_files)} notifications")
            
            # Retorna o mesmo input_data para manter consistência entre tasks_result e notification_result
            return input_data
            
        except Exception as e:
            print(f"\n❌ Error in notification process: {e}")
            return f"Error executing agent: {str(e)}"
