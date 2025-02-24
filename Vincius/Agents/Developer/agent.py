from typing import Dict, Any, List, Optional
from pathlib import Path
from Vincius.Core.brain_model import BrainModel
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.Developer.code_creator import CodeCreator
from Vincius.Agents.Developer.code_reviewer import CodeReviewer

class DeveloperAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config = config
        self.brain = BrainModel()
        self.code_creator = CodeCreator()
        self.code_reviewer = CodeReviewer()
        self.fs_manager = FileSystemManager()

    def execute(self, input_data: Any = None) -> str:
        try:
            print("\n🚀 Starting code generation...")
            
            # Generate and create code files
            result = self.code_creator.create_from_analysis(
                input_data, 
                self.brain, 
                self.config
            )
            
            if not result.saved_files:
                return "No files were created"
            
            print(f"\n📁 Created {len(result.saved_files)} files")
            
            # Verify structure using fs_manager
            if self.fs_manager.verify_structure(result.saved_files, self.brain, self.config):
                print("\n🔍 Starting code review phase...")
                self.code_reviewer.review_files(result.saved_files, self.brain, self.config)
                print("\n✅ Development completed successfully")
            else:
                print("\n⚠️ Project structure verification failed")
            
            return result.content
            
        except Exception as e:
            print(f"\n❌ Error in development process: {e}")
            return f"Error executing agent: {str(e)}"
