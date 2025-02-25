from typing import Dict, Any, Optional
from Vincius.Core.config_manager import ConfigManager
from Vincius.Core.start_step_finder import StartStepFinder
from importlib import import_module

class WorkflowManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.workflow = self.config_manager.get_workflow().get('workflow', {})
        
        # Usar StartStepFinder para determinar o passo inicial
        start_finder = StartStepFinder(self.workflow)
        self.current_step = start_finder.find_start_step()
        
        print(f"✅ Found starting step: {self.current_step}")

    def execute_workflow(self, input_data: Any = None) -> Optional[Dict]:
        """Execute the workflow from the starting step"""
        return self.execute(input_data)  # Use existing execute method
        
    def execute(self, input_data: Any = None) -> Optional[Dict]:
        try:
            print(f"Starting workflow execution from: {self.current_step}")
            
            while self.current_step:
                print("\n" + "=" * 50)
                print(f"Executing step: {self.current_step}")
                print("=" * 50 + "\n")
                
                step_config = self.workflow.get(self.current_step)
                if not step_config:
                    raise ValueError(f"Step not found: {self.current_step}")
                
                # Execute current step
                result = self._execute_step(step_config, input_data)
                
                # Move to next step
                next_step = step_config.get('next_steps', {}).get('success_step')
                if not next_step:
                    print(f"✅ Workflow completed at step: {self.current_step}")
                    return result
                
                self.current_step = next_step
                input_data = result  # Pass result to next step
                
            return input_data
            
        except Exception as e:
            print(f"Error executing workflow: {str(e)}")
            return None

    def _execute_step(self, step_config: Dict, input_data: Any) -> Any:
        """Execute a single workflow step"""
        try:
            action = step_config.get('action')
            if not action:
                raise ValueError("No action defined for step")

            # Handle different action types
            action_type = action.get('type')
            if action_type == 'class_execution':
                return self._execute_class_action(action, input_data)
            else:
                raise ValueError(f"Unsupported action type: {action_type}")

        except Exception as e:
            print(f"Error executing step: {str(e)}")
            raise

    def _execute_class_action(self, action: Dict, input_data: Any) -> Any:
        """Execute a class-based action"""
        try:
            # Import the module
            module_path = action.get('module')
            class_name = action.get('class')
            
            if not module_path or not class_name:
                raise ValueError("Missing module or class name in action config")

            module = import_module(module_path)
            agent_class = getattr(module, class_name)

            # Get agent configuration
            agent_config = action.get('agent_config', {})
            
            # Initialize and execute agent
            agent = agent_class(agent_config)
            result = agent.execute(input_data)
            
            return result

        except Exception as e:
            print(f"Error executing class action: {str(e)}")
            raise