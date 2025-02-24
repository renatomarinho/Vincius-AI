from typing import Dict, Any
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod

class GetMethod(APIMethod):
    def get_method_name(self) -> str:
        return "GET"
    
    def format_request(self, data: Any) -> Dict[str, Any]:
        clean_data = self._ensure_valid_data(data)
        return {
            "method": "GET",
            "params": clean_data,
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }

    def get_method_rules(self) -> Dict[str, Any]:
        return {
            "name": "GET",
            "supports_body": False,
            "idempotent": True,
            "format_rules": [
                "Query parameters must be URL encoded",
                "No request body allowed",
                "Parameters should be simple key-value pairs"
            ],
            "structure": {
                "params": "Optional",
                "headers": "Required"
            }
        }
