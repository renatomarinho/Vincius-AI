class APIRequestPrompts:
    @staticmethod
    def create_request(data: str, method_name: str, api_config: dict) -> str:
        return f"""
Transform this input data into a valid {method_name} API request.

Input Data:
{data}

API Configuration:
Base URL: {api_config['base_url']}
Version: {api_config['version']}
Available Endpoints: {api_config['endpoints']}

Request Schema:
{api_config.get('request_schema', {})}

Create a request following this structure:

FILE: request_data.json
Type: json
Description: API request configuration
Content:
{{
    "endpoint": "[Select appropriate endpoint]",
    "method": "{method_name}",
    "headers": {{ ... }},
    "auth": {{ ... }},
    # For POST/PUT:
    "body": {{
        "name": "[mapped from input]",
        "description": "[mapped from input]",
        "category": "[mapped from input]",
        ... additional fields based on schema
    }},
    # For GET/DELETE:
    "params": {{
        "id": "[if needed]",
        "filter": "[if needed]",
        ... additional parameters based on schema
    }}
}}

Requirements:
1. Map input fields to correct schema properties
2. Include only relevant sections (body/params) based on method
3. Validate against schema requirements
4. Include all required fields
5. Apply proper data types
"""
