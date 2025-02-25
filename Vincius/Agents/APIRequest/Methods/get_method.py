from typing import Dict, Any
import requests
import json
# from Vincius.Agents.APIRequest.Methods.base_method import APIMethod
from pathlib import Path
import time
import datetime

class GetMethod:
    def __init__(self, logger, base_path):
        self.logger = logger
        self.base_path = base_path

    def get_method_name(self) -> str:
        return "GET"

    def execute_request(self, base_url: str, params: Dict[str, Any] = None) -> Any:
        start_time = time.time()
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            try:
                result = response.json()  # Try to parse JSON response
            except json.JSONDecodeError:
                result = response.text  # Return raw text if not JSON
            
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
                "content_length": response.headers.get('content-length'),
                "content_type": response.headers.get('content-type')
            }
            
            # Log the API call
            self.logger.log_file_creation(
                file_path=self.logger.log_file,
                description=f"GET request to {base_url} with params {params}",
                content=json.dumps(log_content, indent=2)
            )
            
            # Save the request and response to a file in the base directory
            file_path = Path(self.base_path) / "get_request_info.json"
            with open(file_path, "w") as f:
                json.dump(log_content, f, indent=2)
            
            print(f"✅ Saved request information to: {file_path}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            return f"Error: API request failed - {str(e)}"
