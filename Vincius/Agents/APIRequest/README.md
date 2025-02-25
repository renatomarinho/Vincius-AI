APIRequest:
    description: Create and format API requests based on input data
    responsible_department: INTEGRATION
    action:
      type: class_execution
      class: APIRequestAgent
      module: Vincius.Agents.APIRequest.agent
      input_key: prompt_output
      output_key: api_request_result
      agent_config:
        method: "GET"
        api_config:
          base_url: "https://api.example.com/v1"
          version: "1.0"
          endpoints:
            resources: "/resources"
            tasks: "/tasks"
            projects: "/projects"
          headers:
            Content-Type: "application/json"
            Accept: "application/json"
          auth:
            type: "bearer"
            token_env: "API_TOKEN"
          request_schema:
            body:
              name:
                type: "string"
                required: true
                description: "Name of the resource"
              description:
                type: "string"
                required: false
                description: "Resource description"
              category:
                type: "string"
                required: true
                enum: ["feature", "bug", "enhancement"]
              status:
                type: "string"
                default: "pending"
            params:
              id:
                type: "string"
                required: true
                description: "Resource identifier"
              filter:
                type: "string"
                required: false
                description: "Filter criteria"
              page:
                type: "integer"
                default: 1
                description: "Page number for pagination"
    next_steps:
      success_step: {}
