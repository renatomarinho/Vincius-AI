"""
Prompt templates for API requests
"""

PUT_REQUEST_PROMPT = """
Create a PUT request body from this input data.
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
6. Make sure the body represents the complete resource state

Generate response in exactly this format:

FILE: Docs/requests/put_request.json
Type: json
Content:
{{
    "endpoint": "[appropriate endpoint from input]",
    "method": "PUT",
    "headers": {headers},
    "body": {{
        [Mapped and validated fields here]
    }}
}}
"""

POST_REQUEST_PROMPT = """
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
    "headers": {headers},
    "body": {{
        [Mapped and validated fields here]
    }}
}}
"""
