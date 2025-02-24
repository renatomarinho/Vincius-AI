from typing import Dict, Any
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod

class PutMethod(APIMethod):
    def get_method_name(self) -> str:
        return "PUT"
    
    def format_request(self, data: Any) -> Dict[str, Any]:
        clean_data = self._ensure_valid_data(data)
        return {
            "method": "PUT",
            "body": clean_data,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }

    def get_method_rules(self) -> Dict[str, Any]:
        return {
            "name": "PUT",
            "supports_body": True,
            "idempotent": True,
            "format_rules": [
                "Full resource representation required",
                "Must be idempotent",
                "Content-Type should match resource type",
                "Body should contain complete resource state"
            ],
            "structure": {
                "body": "Required",
                "headers": "Required"
            }
        }
