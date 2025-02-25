



TaskManager:
    description: Break down technical requirements into clear, actionable tasks
    responsible_department: MANAGER
    action:
      type: class_execution
      class: TaskManagerAgent
      module: Vincius.Agents.TaskManager.agent
      input_key: analysis_result
      output_key: tasks_result
      agent_config:
        model: "gemini-2.0-flash"
        max_tokens: 1024
        temperature: 0.7
        prompt: "Analyze the technical requirements and create a structured task breakdown following the provided guidelines"
        debug_mode: true
        guidelines:
          - "Break down complex features into smaller, manageable tasks"
          - "Create clear and specific task descriptions"
          - "Assign appropriate difficulty levels (Easy/Medium/Hard)"
          - "Categorize tasks by type (Feature/Bug/Enhancement/Documentation/Testing)"
          - "Ensure each task has a unique ID and descriptive title"
          - "Focus on technical implementation details"
          - "Keep task descriptions objective and actionable"
          - "Each task must be implementation-focused"
          - "Include all necessary technical details in descriptions"
          - "Ensure tasks are independent and well-defined"
    next_steps:
      success_step: Notification
