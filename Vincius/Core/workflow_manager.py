from typing import Dict, Any, Optional
from Vincius.Core.workflow_executor import WorkflowExecutor
from .config_manager import ConfigManager
from .start_step_finder import StartStepFinder

class WorkflowManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.steps = self.config_manager.workflow
        self.context = {}
        self.step_finder = StartStepFinder(self.steps)
        
        if not self.steps:
            print("⚠️ No workflow steps found in configuration!")
            print("Please ensure workflow.yaml exists and contains valid workflow steps.")

    def execute_workflow(self) -> None:
        start_step = self.step_finder.find_start_step()
        
        if not self.steps:
            print(f"⚠️ No workflow steps found, will attempt to execute step: {start_step}")
        
        print(f"Starting workflow execution from: {start_step}")
        try:
            executor = WorkflowExecutor(workflow_config=self.steps, context=self.context)
            executor.execute_workflow(start_step)
        except Exception as e:
            print(f"Error during workflow execution: {e}")
            print("Traceback details:")
            import traceback
            print(traceback.format_exc())