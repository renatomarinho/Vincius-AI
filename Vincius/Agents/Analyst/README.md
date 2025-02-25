


  Analysis:
    description: Analyze and document the requirements for the software.
    responsible_department: ANALYSIS
    action:
      type: class_execution
      class: AnalystAgent
      module: Agents.Analyst.agent
      input_key: null
      output_key: analysis_result
      agent_config:
        model: "gemini-2.0-flash"
        max_tokens: 1024
        temperature: 0.7
        prompt: "Analyze these requirements and create a comprehensive technical specification to create GitHub Actions to a Laravel 11 project to running on AWS. Note: Laravel testing are important. Nao preciso de nada muito complexo, escreva toda documentacao em portugues" #Focus on architecture, components, and implementation details."
        guidelines:
          - "Focus on system architecture and components"
          - "Consider scalability and maintainability"
          - "Identify potential technical challenges"
          - "Document all technical requirements clearly"
          - "Provide clear implementation recommendations"
    next_steps:
      success_step: TaskManager