from typing import Dict, Any, List, Optional
import os
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

    def _setup_auth(self, auth_config: Dict[str, Any]) -> tuple[Dict[str, Any], Optional[requests.auth.AuthBase]]:
        """Setup authentication headers and auth object based on configuration"""
        headers = {}
        auth = None

        if not auth_config:
            print("ℹ️ No authentication configured")
            return headers, auth

        auth_type = auth_config.get('type', '').lower()
        
        if auth_type == 'bearer':
            token = auth_config.get('token')
            if not token:
                token_env = auth_config.get('token_env')
                if token_env:
                    token = os.environ.get(token_env)
                    if not token:
                        print(f"⚠️ Bearer token not found in environment variable: {token_env}")
                else:
                    print("⚠️ No token or token_env provided for bearer authentication")
            
            if token:
                headers['Authorization'] = f'Bearer {token}'
                print("✅ Bearer token authentication configured")
            
        elif auth_type == 'basic':
            username = auth_config.get('username')
            password = auth_config.get('password')
            
            if not username or not password:
                username_env = auth_config.get('username_env')
                password_env = auth_config.get('password_env')
                
                if username_env and password_env:
                    username = os.environ.get(username_env)
                    password = os.environ.get(password_env)
                    if not username or not password:
                        print(f"⚠️ Credentials not found in environment variables: {username_env}, {password_env}")
                else:
                    print("⚠️ No credentials provided for basic authentication")
            
            if username and password:
                from requests.auth import HTTPBasicAuth
                auth = HTTPBasicAuth(username, password)
                print("✅ Basic authentication configured")
        
        else:
            print(f"ℹ️ Unknown authentication type: {auth_type}")
        
        return headers, auth

    def _validate_params(self, input_data: Dict[str, Any], param_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and process parameters based on their configuration"""
        validated_params = {}
        
        for param_config in param_configs:
            name = param_config['name']
            required = param_config.get('required', False)
            param_type = param_config.get('type', 'string')
            default = param_config.get('default')
            
            # Get value from input data or use default
            value = input_data.get(name, default)
            
            # Check required parameters
            if required and value is None:
                raise ValueError(f"Required parameter '{name}' is missing")
            
            # Type conversion if needed
            if value is not None:
                try:
                    if param_type == 'integer':
                        value = int(value)
                    elif param_type == 'number':
                        value = float(value)
                    elif param_type == 'boolean':
                        value = bool(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid type for parameter '{name}'. Expected {param_type}")
                
                validated_params[name] = value
        
        return validated_params

    def _merge_dynamic_params(self, api_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge static config parameters with dynamic input parameters"""
        merged_config = api_config.copy()
        
        # If input_data contains API configuration, merge it
        if 'api_config' in input_data:
            dynamic_config = input_data['api_config']
            
            # Update base URL if provided
            if 'base_url' in dynamic_config:
                merged_config['base_url'] = dynamic_config['base_url']
            
            # Merge or override parameters
            if 'params' in dynamic_config:
                if 'params' not in merged_config:
                    merged_config['params'] = {}
                
                # Merge URL parameters
                if 'url_params' in dynamic_config['params']:
                    merged_config['params']['url_params'] = [
                        *merged_config.get('params', {}).get('url_params', []),
                        *dynamic_config['params']['url_params']
                    ]
                
                # Merge query parameters
                if 'query_params' in dynamic_config['params']:
                    merged_config['params']['query_params'] = [
                        *merged_config.get('params', {}).get('query_params', []),
                        *dynamic_config['params']['query_params']
                    ]
            
            # Update authentication if provided
            if 'auth' in dynamic_config:
                merged_config['auth'] = dynamic_config['auth']
        
        return merged_config

    def execute(self, input_data: Any = None) -> Any:
        try:
            print(f"\n🌐 Creating {self.method_name} request...")
            
            if self.method_name in ['GET', 'DELETE']:
                api_config = self.config.get('api_config', {})
                
                # Process dynamic configuration from input_data
                if isinstance(input_data, dict):
                    api_config = self._merge_dynamic_params(api_config, input_data)
                    # Remove api_config from input_data to avoid processing it as parameters
                    request_params = {k: v for k, v in input_data.items() if k != 'api_config'}
                else:
                    request_params = input_data if isinstance(input_data, dict) else {}
                
                base_url = api_config.get('base_url')
                if not base_url:
                    return f"Error: Base URL not provided in api_config for {self.method_name} request"
                
                # Process input parameters
                params_config = api_config.get('params', {})
                
                # Validate URL parameters
                url_params = self._validate_params(
                    request_params,
                    params_config.get('url_params', [])
                )
                
                # Validate query parameters
                query_params = self._validate_params(
                    request_params,
                    params_config.get('query_params', [])
                )
                
                # Setup authentication
                headers, auth = self._setup_auth(api_config.get('auth', {}))
                
                print(f"🔍 Using dynamic configuration:")
                print(f"   Base URL: {base_url}")
                print(f"   URL Parameters: {url_params}")
                print(f"   Query Parameters: {query_params}")
                
                # Execute the request using appropriate Method
                result = self.method.execute_request(
                    base_url=base_url,
                    params={**url_params, **query_params},
                    headers=headers,
                    auth=auth
                )
                
                return result
            
            elif self.method_name in ['POST', 'PUT']:
                api_config = self.config.get('api_config', {})
                
                # Process dynamic configuration from input_data
                if isinstance(input_data, dict):
                    api_config = self._merge_dynamic_params(api_config, input_data)
                    # Remove api_config from input_data to avoid processing it as parameters
                    request_params = {k: v for k, v in input_data.items() if k != 'api_config'}
                else:
                    request_params = input_data if isinstance(input_data, dict) else {}
                
                base_url = api_config.get('base_url')
                if not base_url:
                    return f"Error: Base URL not provided in api_config for {self.method_name} request"
                
                # Process input parameters
                params_config = api_config.get('params', {})
                
                # Validate URL parameters
                url_params = self._validate_params(
                    request_params,
                    params_config.get('url_params', [])
                )
                
                # Validate query parameters
                query_params = self._validate_params(
                    request_params,
                    params_config.get('query_params', [])
                )
                
                # Extract body data from request_params or use specified body
                body = api_config.get('body', {})
                if 'body' in request_params:
                    body = request_params.pop('body')  # Extract body from params
                
                # Setup authentication
                headers, auth = self._setup_auth(api_config.get('auth', {}))
                
                # Add custom headers if provided
                if 'headers' in api_config:
                    headers.update(api_config['headers'])
                
                print(f"🔍 Using dynamic configuration:")
                print(f"   Base URL: {base_url}")
                print(f"   URL Parameters: {url_params}")
                print(f"   Query Parameters: {query_params}")
                print(f"   Body: {body}")
                
                # Execute the POST/PUT request
                result = self.method.execute_request(
                    base_url=base_url,
                    body=body,
                    params={**url_params, **query_params},
                    headers=headers,
                    auth=auth
                )
                
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
