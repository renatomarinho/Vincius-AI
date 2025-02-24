from pathlib import Path
from typing import Dict, Any, NamedTuple, List, Optional, Callable
from Vincius.Core.file_system_manager import FileSystemManager
from Core.content_parser import ContentParser
from Vincius.Agents.base_agent import BaseAgent

class CreationResult(NamedTuple):
    content: str
    saved_files: List[Path]

class CodeCreator(BaseAgent):
    def __init__(self):
        super().__init__({})
        self.fs_manager = FileSystemManager()

    def create_from_analysis(self, input_data: Any, brain: Any, config: Dict) -> CreationResult:
        """Create code files from analysis with automatic retry"""
        try:
            self.brain = brain
            self.config = config
            prompt = self._generate_prompt(str(input_data), config)
            
            # Use retry mechanism from BaseAgent
            result = self._retry_on_failure(
                prompt=prompt,
                brain=brain,
                error_msg="Failed to generate code implementation"
            )
            
            if not result:
                return CreationResult("", [])

            # Process content using ContentParser
            saved_files = self.fs_manager.process_content(
                result,
                brain=brain,
                config=config,
                retry_prompt=prompt
            )

            return CreationResult(result, saved_files)

        except Exception as e:
            print(f"❌ Error in create_from_analysis: {e}")
            return CreationResult("", [])

    def _generate_prompt(self, input_data: str, config: Dict) -> str:
        """Generate creation prompt with file-based format"""
        guidelines = config.get('guidelines', [])
        guidelines_text = "\n".join(f"- {g}" for g in guidelines)
        
        return f"""
Based on this analysis, generate implementation code:

{input_data}

Follow these guidelines:
{guidelines_text}

Provide your implementation using this format for each file:

FILE: path/to/file.ext
Type: file_type
Description: Brief description of the file's purpose
Content:
[Complete implementation code here]

You can create multiple files by repeating this format.
Each file must be complete and properly structured.
Include all necessary files for the implementation.
"""
