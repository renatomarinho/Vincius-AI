from typing import Dict, Any
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod

class PostMethod(APIMethod):
    def get_method_name(self) -> str:
        return "POST"

    def get_method_prompt(self, input_data: Any, api_config: Dict) -> str:
        schema = api_config.get('request_schema', {}).get('body', {})
        return f"""
Create a POST request body from this input data.
Map the fields according to the API schema.

Input Data:
{input_data}

Required Schema:
{schema}

Format the request body following these rules:
1. Include all required fields from schema
2. Validate field types
3. Use proper data structures
4. Follow API naming conventions
5. Include only valid fields

Generate response in exactly this format:

FILE: docs/requests/post_request.json
Type: json
Content:
{{
    "endpoint": "[appropriate endpoint from input]",
    "method": "POST",
    "headers": {api_config.get('headers', {})},
    "body": {{
        [Mapped and validated fields here]
    }}
}}
"""

    def format_request(self, data: Any) -> Dict[str, Any]:
        clean_data = self._ensure_valid_data(data)
        return {
            "method": "POST",
            "body": clean_data,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }

    def get_method_rules(self) -> Dict[str, Any]:
        return {
            "name": "POST",
            "supports_body": True,
            "idempotent": False,
            "format_rules": [
                "Request body required",
                "Not idempotent - multiple calls may create multiple resources",
                "Content-Type must match request body format",
                "Body should contain new resource data",
                "May return new resource ID/location"
            ],
            "structure": {
                "body": "Required",
                "headers": "Required"
            }
        }
