import importlib
from typing import Dict, Any, Optional
import json
from pathlib import Path

class WorkflowExecutor:
    def __init__(self, workflow_config: Dict[str, Any], context: Dict[str, Any]):
        self.workflow = workflow_config
        self.workflow_data = {}
        self.context = context

    def _get_agent_instance(self, class_name: str, module_name: str):
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls
        except Exception as e:
            print(f"Error loading agent class: {e}")
            raise

    def _save_memory(self, step_name: str, data: Dict[str, Any]):
        memory_file = self.memory_path / f"{step_name}_memory.json"
        with open(memory_file, 'w') as f:
            json.dump(data, f, indent=2)

    def execute_step(self, step_name: str) -> bool:
        print(f"\n{'='*50}")
        print(f"Executing step: {step_name}")
        print(f"{'='*50}\n")
        
        try:
            step_config = self.workflow[step_name]
            action = step_config['action']
            
            class_name = action['class']
            module_name = action['module']
            agent_config = action.get('agent_config', {})
            
            print(f"Attempting to load agent {class_name} from module {module_name}")
            
            try:
                cls = self._get_agent_instance(class_name, module_name)
                agent = cls(agent_config)
            except Exception as e:
                print(f"Failed to initialize agent: {e}")
                return False
            
            input_key = action.get('input_key')
            input_data = self.workflow_data.get(input_key) if input_key else None
            
            try:
                result = agent.execute(input_data)
                if not result:
                    print("Agent returned empty result")
                    return False
                    
                output_key = action.get('output_key')
                if output_key:
                    self.workflow_data[output_key] = result
                
                return True
                
            except Exception as e:
                print(f"Agent execution failed: {e}")
                return False
            
        except Exception as e:
            print(f"Error executing step: {e}")
            return False

    def execute_workflow(self, start_step: str) -> None:
        executed_steps = set()

        def _execute_chain(step_name: str):
            print(f"Attempting to execute chain for step: {step_name}")
            if step_name in executed_steps:
                print(f"Step {step_name} already executed, skipping.")
                return
            if self.execute_step(step_name):
                executed_steps.add(step_name)
                next_steps = self.workflow[step_name]['next_steps']
                print(f"Next steps for {step_name}: {next_steps}")
                if isinstance(next_steps, dict):
                    success_step = next_steps.get('success_step')
                    if success_step:
                        if isinstance(success_step, dict) and not success_step:
                            print("End of workflow.")
                            return  # Empty dict means end of workflow
                        print(f"Executing success step: {success_step}")
                        _execute_chain(success_step)
                elif isinstance(next_steps, list):
                    for next_step in next_steps:
                        print(f"Executing next step: {next_step}")
                        _execute_chain(next_step)

        _execute_chain(start_step)