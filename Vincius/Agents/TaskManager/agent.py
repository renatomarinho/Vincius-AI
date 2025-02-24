from typing import Dict, Any
import logging
import traceback
from pathlib import Path
from Vincius.Core.brain_model import BrainModel
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.TaskManager.task_creator import TaskCreator

class TaskManagerAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.brain = BrainModel()
        self.task_creator = TaskCreator()
        self.fs_manager = FileSystemManager()

    def execute(self, input_data: Any = None) -> str:
        try:
            print("\n📋 Starting task breakdown...")
            
            if not input_data:
                return "Error: No analysis result provided"

            # Create and validate tasks
            tasks = self.task_creator.create_project_tasks(
                str(input_data),
                self.brain,
                self.config
            )
            
            if not tasks:
                return "Error: Failed to create tasks"

            print("✅ Tasks created successfully")
            return tasks
            
        except Exception as e:
            print(f"\n❌ Error in task creation process: {e}")
            return f"Error executing agent: {str(e)}"
