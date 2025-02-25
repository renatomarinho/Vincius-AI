


Development:
    description: Develop the software based on the analyzed requirements.
    responsible_department: DEVELOPMENT
    action:
      type: class_execution
      class: DeveloperAgent
      module: Agents.Developer.agent
      input_key: analysis_result
      output_key: development_output
      agent_config:
        model: "gemini-2.0-flash"
        max_tokens: 2048
        temperature: 0.9
        prompt: "Based on the technical analysis, implement the software following best practices and design patterns. Create all necessary files and components."
        guidelines:
          - "Develop using a main class"
          - "Follow SOLID architecture principles"
          - "Ensure code is modular and reusable"
          - "Include proper documentation"
          - "Implement error handling"
          - "Write clean, maintainable code"
    next_steps:
      success_step: Testing