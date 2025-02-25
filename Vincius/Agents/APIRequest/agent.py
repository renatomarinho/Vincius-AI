from typing import Dict, Any
from Vincius.Core.brain_model import BrainModel
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.APIRequest.api_creator import APICreator
from Vincius.Agents.APIRequest.Methods.get_method import GetMethod
from Vincius.Agents.APIRequest.Methods.put_method import PutMethod
from Vincius.Agents.APIRequest.Methods.post_method import PostMethod
from Vincius.Agents.APIRequest.Methods.delete_method import DeleteMethod
import requests
import json
from Vincius.Core.logger_base import LoggerBase
import uuid
from Vincius.Core.config_manager import ConfigManager

class APIRequestAgent(BaseAgent):
    METHOD_MAPPING = {
        'GET': GetMethod,
        'PUT': PutMethod,
        'POST': PostMethod,
        'DELETE': DeleteMethod
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "APIRequest"  # Set name before initializing other components
        self.agent_uuid = str(uuid.uuid4()) # Initialize agent_uuid here
        
        # Initialize base directory from config
        config_manager = ConfigManager()
        base_dir_key = config.get('base_dir_key', '').lower()
        self.base_dir = config_manager.get_base_path(base_dir_key)
        
        self.brain = BrainModel()
        self.api_creator = APICreator()
        
        # Get HTTP method from config
        self.method_name = config.get('method', 'GET').upper()
        if self.method_name not in self.METHOD_MAPPING:
            print(f"⚠️ Invalid method {self.method_name}, defaulting to GET")
            self.method_name = 'GET'
            
        # Initialize logger
        self.logger = LoggerBase(self.base_dir, self.name, self.agent_uuid)
            
        # Initialize method handler
        method_class = self.METHOD_MAPPING[self.method_name]
        self.method = method_class(self.logger, self.base_dir)
        print(f"✅ Using {self.method_name} method handler")

    def execute(self, input_data: Any = None) -> Any:
        try:
            print(f"\n🌐 Creating {self.method_name} request...")
            
            if self.method_name == 'GET':
                # Directly make the GET request
                api_config = self.config.get('api_config', {})
                base_url = api_config.get('base_url')
                if not base_url:
                    return "Error: Base URL not provided in api_config"
                
                # Include parameters from input_data if provided
                params = input_data if isinstance(input_data, dict) else {}
                
                # Execute the GET request using GetMethod
                result = self.method.execute_request(base_url, params)
                    
                return result
                
            else:
                if not input_data:
                    return "Error: No request data provided"

                # Create request using appropriate method
                request = self.api_creator.create_request(
                    input_data,
                    self.method,
                    self.brain,
                    self.config
                )
                
                if not request:
                    return "Error: Failed to create request"

                print(f"✅ {self.method_name} request created successfully")
                return request
            
        except Exception as e:
            print(f"\n❌ Error in API request creation: {e}")
            return f"Error executing agent: {str(e)}"
