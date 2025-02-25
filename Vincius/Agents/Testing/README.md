






  Testing:
    description: Test the developed software to ensure it meets the requirements.
    responsible_department: TESTING
    action:
      type: class_execution
      class: TesterAgent
      module: Agents.Testing.agent
      input_key: development_output
      output_key: testing_report
      agent_config:
        model: "gemini-2.0-flash"
        max_tokens: 512
        temperature: 0.8
        prompt: "Analyze the code and create comprehensive tests. Focus on functionality, edge cases, and potential failure points."
        guidelines:
          - "Cover all critical functionality"
          - "Include unit and integration tests"
          - "Test edge cases and error scenarios"
          - "Verify performance requirements"
          - "Document test coverage and results"
        test_types: ["unit", "integration", "regression"]
    next_steps:
      failure_step: BugFixing
      success_step: Deployment