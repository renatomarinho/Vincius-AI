from pathlib import Path
from typing import Dict, Any, NamedTuple, List, Optional
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.Developer.prompts import DeveloperPrompts

class CreationResult(NamedTuple):
    content: str
    saved_files: List[Path]

class CodeCreator:  # Remove BaseAgent inheritance
    def __init__(self):
        self.fs_manager = FileSystemManager()
        print("🔧 Initialized CodeCreator")

    def create_from_analysis(self, input_data: Any, brain: Any, config: Dict) -> CreationResult:
        """Create code files from analysis"""
        try:
            prompt = DeveloperPrompts.code_creation(str(input_data), config.get('guidelines', []))
            
            # Generate code implementation
            result = brain.generate(prompt, config)
            
            if not result:
                return CreationResult("", [])

            # Process content using ContentParser
            saved_files = self.fs_manager.process_content(
                result,
                brain=brain,
                config=config,
                retry_prompt=prompt
            )

            # Get recent file operations from logger
            recent_files = self.fs_manager.logger.get_recent_files()
            print("\n📝 Recently created/modified files:")
            for log in recent_files:
                print(f"- {log['file_path']} ({log['operation']} at {log['timestamp']})")

            return CreationResult(result, saved_files)

        except Exception as e:
            print(f"❌ Error in create_from_analysis: {e}")
            return CreationResult("", [])
