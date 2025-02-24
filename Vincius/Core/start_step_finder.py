class StartStepFinder:
    def __init__(self, steps: dict):
        self.steps = steps or {}  # Handle None case
        self.default_step = "Analysis"  # Set default starting step

    def find_start_step(self) -> str:
        """Find the starting step or return default"""
        # If no steps configured, return default
        if not self.steps:
            print(f"⚠️ No workflow steps found, using default step: {self.default_step}")
            return self.default_step

        next_steps = set()
        # Collect all steps that are mentioned as next steps
        for step_info in self.steps.values():
            if 'next_steps' in step_info:
                for _, next_step in step_info['next_steps'].items():
                    if isinstance(next_step, str):
                        next_steps.add(next_step)
                    elif isinstance(next_step, dict):
                        step_name = next_step.get('name')
                        if isinstance(step_name, str):
                            next_steps.add(step_name)

        # Find first step that isn't mentioned as a next step
        for step in self.steps.keys():
            if step not in next_steps:
                print(f"✅ Found starting step: {step}")
                return step

        # If no start step found in workflow, use default
        print(f"⚠️ No start step found in workflow, using default: {self.default_step}")
        return self.default_step