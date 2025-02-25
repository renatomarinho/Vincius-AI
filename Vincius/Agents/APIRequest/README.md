# API Request Agent

A specialized agent for handling HTTP requests to external APIs, with support for dynamic parameters, authentication, and detailed logging.

## Features

- Supports multiple HTTP methods (GET, POST, PUT, DELETE).
- Dynamic URL parameter handling.
- Query parameter validation.
- Bearer Token and Basic Auth support.
- Detailed request logging.
- Integration with other agents.
- Environment variable support for sensitive data.
- YAML-based configuration.

## Configuration

### Basic Setup

```yaml
agent_config:
  base_dir_key: "API"
  method: "GET"
  api_config:
    base_url: "https://api.example.com/v1/users/{user_id}/posts/{post_id}"
    params:
      # URL Parameters (Path Parameters)
      url_params:
        - name: "user_id"
          required: true
          type: "string"
          description: "User identifier"
        - name: "post_id"
          required: true
          type: "string"
          description: "Post identifier"
      
      # Query Parameters
      query_params:
        - name: "filter"
          required: false
          type: "string"
          default: "recent"
          description: "Post filter"
        - name: "limit"
          required: false
          type: "integer"
          default: 10
          description: "Results limit"
```

### Workflow Integration

```yaml
workflow:
  APIRequest:
    description: Creates and formats API requests based on input data.
    responsible_department: INTEGRATION
    action:
      type: class_execution
      class: APIRequestAgent
      module: Vincius.Agents.APIRequest.agent
      input_key: prompt_output
      output_key: api_request_result
      agent_config:
        base_dir_key: "API"
        method: "GET"
        api_config:
          base_url: "https://api.example.com/v1/users/{user_id}/posts/{post_id}"
          auth:
            # Option 1: Bearer Token
            type: "bearer"
            # token: "YOUR_API_TOKEN" # Direct token (not recommended for production)
            token_env: "API_TOKEN"  # Token via environment variable (recommended)

            # Option 2: Basic Auth
            # type: "basic"
            # username: "YOUR_USERNAME"  # Direct credentials (not recommended for production)
            # password: "YOUR_PASSWORD"
            # username_env: "API_USERNAME"  # Via environment variable
            # password_env: "API_PASSWORD"
          params:
            # URL Parameters (Path Parameters)
            url_params:
              - name: "user_id"
                required: true
                type: "string"
                description: "User identifier"
              - name: "post_id"
                required: true
                type: "string"
                description: "Post identifier"
            
            # Query Parameters
            query_params:
              - name: "filter"
                required: false
                type: "string"
                default: "recent"
                description: "Post filter"
              - name: "limit"
                required: false
                type: "integer"
                default: 10
                description: "Results limit"
    next_steps:
      success_step: {}

## Integration with Other Agents

The `APIRequest` agent can receive parameters from other agents. Here's an example of how to pass parameters:

### Simple Parameter Values

```json
{
    "api_config": {
        "base_url": "https://api.newservice.com/v2/users/{user_id}",
        "params": {
            "url_params": [
                {
                    "name": "user_id",
                    "required": true,
                    "type": "string"
                }
            ],
            "query_params": [
                {
                    "name": "include_details",
                    "required": false,
                    "type": "boolean",
                    "default": true
                }
            ]
        },
        "auth": {
            "type": "bearer",
            "token_env": "NEW_SERVICE_TOKEN"
        }
    },
    "user_id": "789",
    "include_details": true
}
```
