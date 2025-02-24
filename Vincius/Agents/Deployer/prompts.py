class DeployerPrompts:
    """Prompts for deployment process"""
    
    @staticmethod
    def create_deployment_plan(input_data: str) -> str:
        return f"""
Analyze the implementation and create a deployment plan.

Input:
{input_data}

Create a deployment plan considering:
1. Required environment setup
2. Deployment steps
3. Rollback procedures
4. Monitoring requirements
5. Post-deployment verification

Format your response with clear sections and steps.
"""
