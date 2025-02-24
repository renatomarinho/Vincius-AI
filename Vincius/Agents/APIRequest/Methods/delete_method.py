from typing import Dict, Any
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod

class DeleteMethod(APIMethod):
    def get_method_name(self) -> str:
        return "DELETE"
    
    def format_request(self, data: Any) -> Dict[str, Any]:
        clean_data = self._ensure_valid_data(data)
        return {
            "method": "DELETE",
            "params": clean_data,  # Usually just needs resource identifier
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }

    def get_method_rules(self) -> Dict[str, Any]:
        return {
            "name": "DELETE",
            "supports_body": False,
            "idempotent": True,
            "format_rules": [
                "Resource identifier required",
                "Body typically not needed",
                "Idempotent - multiple calls should have same effect",
                "May return 204 No Content",
                "Should confirm resource existence before delete"
            ],
            "structure": {
                "params": "Required (resource ID)",
                "headers": "Required"
            }
        }
