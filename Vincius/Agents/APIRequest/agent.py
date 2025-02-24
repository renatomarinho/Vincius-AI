from typing import Dict, Any
from Vincius.Core.brain_model import BrainModel
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.APIRequest.api_creator import APICreator
from Vincius.Agents.APIRequest.Methods import GetMethod, PutMethod, PostMethod, DeleteMethod

class APIRequestAgent(BaseAgent):
    METHOD_MAPPING = {
        'GET': GetMethod,
        'PUT': PutMethod,
        'POST': PostMethod,
        'DELETE': DeleteMethod
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.brain = BrainModel()
        self.api_creator = APICreator()
        
        # Get HTTP method from config
        self.method_name = config.get('method', 'GET').upper()
        if self.method_name not in self.METHOD_MAPPING:
            print(f"⚠️ Invalid method {self.method_name}, defaulting to GET")
            self.method_name = 'GET'
            
        # Initialize method handler
        self.method = self.METHOD_MAPPING[self.method_name]()
        print(f"✅ Using {self.method_name} method handler")

    def execute(self, input_data: Any = None) -> Any:
        try:
            print(f"\n🌐 Creating {self.method_name} request...")
            
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
