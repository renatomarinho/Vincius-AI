from typing import Dict, Any, Optional
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod
import requests
import json
from pathlib import Path
import time
import datetime
import re

class PostMethod(APIMethod):
    def __init__(self, logger, base_path):
        super().__init__(logger)
        self.base_path = base_path

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

FILE: Docs/requests/post_request.json
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

    def _process_url_params(self, url: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Process URL parameters and return the formatted URL and remaining query params"""
        # Find all template parameters in the URL {param_name}
        template_params = re.findall(r'\{([^}]+)\}', url)
        query_params = params.copy()
        
        # Replace template parameters with values from params
        for param in template_params:
            if param in params:
                url = url.replace(f'{{{param}}}', str(params[param]))
                query_params.pop(param)  # Remove used parameter from query params
        
        return url, query_params

    def execute_request(self, base_url: str, body: Dict[str, Any] = None, params: Dict[str, Any] = None, 
                        headers: Dict[str, Any] = None, auth: Optional[requests.auth.AuthBase] = None) -> Any:
        start_time = time.time()
        try:
            # Process URL parameters if any
            params = params or {}
            url, query_params = self._process_url_params(base_url, params)
            
            # Make sure we have proper headers for JSON content
            if headers is None:
                headers = {}
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            if 'Accept' not in headers:
                headers['Accept'] = 'application/json'
            
            # Convert body to JSON if it's a dictionary
            json_body = None
            if body:
                if isinstance(body, dict):
                    json_body = body
                else:
                    # Try to parse as JSON if it's a string
                    try:
                        json_body = json.loads(body) if isinstance(body, str) else body
                    except json.JSONDecodeError:
                        return f"Error: Invalid JSON body - {body}"
            
            # Execute POST request
            response = requests.post(
                url, 
                json=json_body,
                params=query_params, 
                headers=headers, 
                auth=auth
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Parse response
            try:
                result = response.json()  # Try to parse JSON response
            except json.JSONDecodeError:
                result = response.text  # Return raw text if not JSON
            
            # Format the start time using timezone-aware objects
            start_time_utc = datetime.datetime.fromtimestamp(start_time, tz=datetime.timezone.utc)
            start_time_formatted = start_time_utc.strftime('%a, %d %b %Y %H:%M:%S UTC')
            
            # Prepare content for logging and saving
            log_content = {
                "request_url": url,
                "request_params": query_params,
                "request_body": json_body,
                "response": result,
                "http_status_code": response.status_code,
                "request_start_time": start_time_formatted,
                "request_start_time_timestamp": start_time,
                "total_request_time": total_time,
                "content_type": response.headers.get('content-type'),
                "location": response.headers.get('location')  # Often contains the URL of created resource
            }
            
            # Log the API call
            self.logger.log_file_creation(
                file_path=self.logger.log_file,
                description=f"POST request to {url}",
                content=json.dumps(log_content, indent=2)
            )
            
            # Save the request and response to a file in the base directory
            file_path = Path(self.base_path) / "post_request_info.json"
            with open(file_path, "w") as f:
                json.dump(log_content, f, indent=2)
            
            print(f"✅ Saved POST request information to: {file_path}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            return f"Error: API request failed - {str(e)}"

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
