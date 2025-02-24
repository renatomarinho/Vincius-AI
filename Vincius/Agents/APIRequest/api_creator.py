from typing import Dict, Any, Optional
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod
from Vincius.Agents.APIRequest.prompts import APIRequestPrompts

class APICreator:
    def __init__(self):
        self.fs_manager = FileSystemManager()

    def create_request(self, data: Any, method: APIMethod, brain: Any, config: Dict) -> Optional[Dict[str, Any]]:
        """Create API request based on method and data"""
        try:
            print(f"\n🔄 Creating {method.get_method_name()} request...")
            
            # Get method-specific prompt
            prompt = method.get_method_prompt(data, config.get('api_config', {}))
            
            # Generate request content
            response = brain.generate(prompt, config)
            if not response:
                print("❌ Failed to generate request")
                return None

            # Format and save request
            request = method.format_request(response)
            method.save_request(request, data)
            
            return request
            
        except Exception as e:
            print(f"❌ Error creating request: {e}")
            return None
