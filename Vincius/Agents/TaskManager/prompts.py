from typing import Dict, List

class TaskManagerPrompts:
    """Prompts for task management and creation"""
    
    @staticmethod
    def create_tasks_csv(analysis: str, debug: bool = False) -> str:
        if not analysis:
            raise ValueError("Analysis string cannot be empty")
            
        debug_instructions = """
- Include detailed error messages for any validation failures
- Add debug information in comments for each task
- Validate input data format before processing
- Check for data consistency and completeness
""" if debug else ""

        return f"""
As a technical project manager, analyze this technical specification and break it down into actionable tasks.
Follow these guidelines strictly:
{debug_instructions}
- Break down complex features into smaller, manageable tasks
- Create clear and specific task descriptions
- Assign appropriate difficulty levels (Easy/Medium/Hard)
- Categorize tasks by type (Feature/Bug/Enhancement/Documentation/Testing)
- Ensure each task has a unique ID and descriptive title
- Focus on technical implementation details
- Keep task descriptions objective and actionable
- Validate all input data before processing

Technical Analysis:
{analysis}

Create a task list using exactly these columns:
- id: Task ID in format T001, T002, etc
- title: Short descriptive title of the task
- description: Technical implementation details of what needs to be done
- task_type: One of [Feature, Bug, Enhancement, Documentation, Testing]
- difficulty: One of [Easy, Medium, Hard]

If any errors are found, format the response as:
ERROR: [Error description]

Otherwise, format your response exactly like this:
FILE: Docs/project_tasks.csv
Type: csv
Description: Project task breakdown
Content:
id,title,description,task_type,difficulty
[Task list following the guidelines...]
"""

    @staticmethod
    def review_tasks(tasks: str) -> str:
        return f"""
Review these tasks for completeness and technical feasibility.

Tasks:
{tasks}

Verify:
1. All components from analysis are covered
2. Tasks are properly broken down
3. Technical details are clear
4. Task types are appropriate
5. Difficulty levels are realistic

If improvements needed, respond with:
IMPROVEMENTS NEEDED:
[List specific improvements]

If tasks are complete and well-defined, respond with:
"VALIDATION_PASSED: Tasks are well-defined and ready for development"
"""

    @staticmethod
    def get_debug_info() -> str:
        """Return debugging instructions and validation rules"""
        return """
Debug Information Format:
DEBUG_INFO:
- Validation Rules: [list of applied rules]
- Data Format: [expected format]
- Error Checks: [performed validations]
- Processing Steps: [steps taken]
"""
