# API Request Agent

## Overview
The API Request Agent is designed to automatically transform input data into properly formatted HTTP requests. It supports multiple HTTP methods and handles request formatting according to API specifications.

## Core Components

### 1. APIRequestAgent (agent.py)
Main agent class that:
- Handles method selection based on configuration
- Manages request creation flow
- Integrates with the brain model
```yaml
agent_config:
  method: "POST"  # Supported: GET, POST, PUT, DELETE
  api_config:
    base_url: "https://api.example.com/v1"
```

### 2. APICreator (api_creator.py)
Request generation service that:
- Creates requests using appropriate method
- Handles prompt generation
- Saves request documentation

### 3. HTTP Methods
Located in `/methods` directory:
- **base_method.py**: Abstract base class for all HTTP methods
- **get_method.py**: GET request handling
- **post_method.py**: POST request handling
- **put_method.py**: PUT request handling
- **delete_method.py**: DELETE request handling

Each method implements:
```python
def get_method_name(self) -> str
def get_method_prompt(self, input_data, api_config) -> str
def format_request(self, data) -> Dict
def get_method_rules(self) -> Dict
```

## Configuration

### Basic Configuration
```yaml
APIRequest:
  action:
    agent_config:
      method: "POST"
      api_config:
        base_url: "https://api.example.com/v1"
        version: "1.0"
```

### Request Schema
```yaml
request_schema:
  body:  # For POST/PUT
    name:
      type: "string"
      required: true
    status:
      type: "string"
      default: "pending"
  params:  # For GET/DELETE
    id:
      type: "string"
      required: true
```

## Usage Examples

### POST Request
```python
config = {
    "method": "POST",
    "api_config": {
        "base_url": "https://api.example.com",
        "endpoints": {
            "tasks": "/tasks"
        }
    }
}

agent = APIRequestAgent(config)
result = agent.execute(task_data)
```

### GET Request
```python
config = {
    "method": "GET",
    "api_config": {
        "base_url": "https://api.example.com",
        "params": {
            "id": "required"
        }
    }
}

agent = APIRequestAgent(config)
result = agent.execute({"id": "123"})
```

## Output Format
The agent generates JSON files in `/docs/requests/` with this structure:
```json
{
    "method": "POST",
    "request": {
        "endpoint": "/tasks",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "name": "Task Name",
            "description": "Task Description"
        }
    },
    "original_input": {
        // Original input data
    }
}
```

## Method Characteristics

### GET
- Query parameters
- No request body
- URL encoded parameters
- Idempotent

### POST
- Request body required
- Creates new resources
- Not idempotent
- Returns new resource ID

### PUT
- Full resource update
- Request body required
- Idempotent
- Complete resource state

### DELETE
- Resource identifier required
- Usually no body
- Idempotent
- Returns 204 No Content

## Extending
To add a new HTTP method:
1. Create new class in `/methods`
2. Inherit from `APIMethod`
3. Implement required methods
4. Add to `METHOD_MAPPING` in agent.py

## Error Handling
- Invalid method defaults to GET
- Missing configuration logs warning
- Request generation failures return None
- All errors are logged