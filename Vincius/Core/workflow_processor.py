

class WorkflowProcessor:
    def __init__(self, workflow_data: dict):
        self.workflow_data = workflow_data

    def process_workflow(self) -> dict:
        steps = {}
        for step_name, step_info in self.workflow_data.items():
            if not step_info or not isinstance(step_info, dict):
                raise ValueError(f"Incomplete or invalid data for step: {step_name}")
            description = step_info.get('description')
            responsible_department = step_info.get('responsible_department')
            action = step_info.get('action', {})
            next_steps = step_info.get('next_steps', {})
            if not description or not responsible_department:
                raise ValueError(f"Incomplete data for step: {step_name}")
            steps[step_name] = {
                'description': description,
                'department': responsible_department,
                'action': action,
                'next_steps': next_steps
            }
        return steps