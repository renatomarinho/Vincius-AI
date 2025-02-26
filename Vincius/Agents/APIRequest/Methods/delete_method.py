from typing import Dict, Any, Optional
from Vincius.Agents.APIRequest.Methods.base_method import APIMethod
import requests
import json
from pathlib import Path
import time
import datetime
import re

class DeleteMethod(APIMethod):
    def __init__(self, logger, base_path):
        super().__init__(logger)
        self.base_path = base_path

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

    def execute_request(self, base_url: str, params: Dict[str, Any] = None, headers: Dict[str, Any] = None, auth: Optional[requests.auth.AuthBase] = None) -> Any:
        start_time = time.time()
        try:
            # Process URL parameters if any
            params = params or {}
            url, query_params = self._process_url_params(base_url, params)
            
            response = requests.delete(url, params=query_params, headers=headers, auth=auth)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Try to parse JSON response if available
            try:
                result = response.json()
            except json.JSONDecodeError:
                # For 204 No Content or other non-JSON responses
                result = {"status": "success", "status_code": response.status_code}
            
            # Format the start time using timezone-aware objects
            start_time_utc = datetime.datetime.fromtimestamp(start_time, tz=datetime.timezone.utc)
            start_time_formatted = start_time_utc.strftime('%a, %d %b %Y %H:%M:%S UTC')
            
            # Prepare content for logging and saving
            log_content = {
                "request_url": base_url,
                "request_params": params,
                "response": result,
                "http_status_code": response.status_code,
                "request_start_time": start_time_formatted,
                "request_start_time_timestamp": start_time,
                "total_request_time": total_time,
                "content_type": response.headers.get('content-type')
            }
            
            # Log the API call
            self.logger.log_file_creation(
                file_path=self.logger.log_file,
                description=f"DELETE request to {base_url} with params {params}",
                content=json.dumps(log_content, indent=2)
            )
            
            # Save the request and response to a file in the base directory
            file_path = Path(self.base_path) / "delete_request_info.json"
            with open(file_path, "w") as f:
                json.dump(log_content, f, indent=2)
            
            print(f"✅ Saved DELETE request information to: {file_path}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            return f"Error: API request failed - {str(e)}"

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
