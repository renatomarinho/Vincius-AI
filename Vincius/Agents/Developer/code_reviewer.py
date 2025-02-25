from pathlib import Path
from typing import List, Dict, Any, Optional
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.Developer.prompts import DeveloperPrompts

class CodeReviewer:
    def __init__(self):
        self.fs_manager = FileSystemManager()
        
    def review_files(self, files: List[Path], brain: Any, config: Dict[str, Any]) -> bool:
        """Review a list of files and suggest improvements"""
        try:
            print(f"\n🔍 Starting code review phase...")
            
            # Get all files from directory if not provided
            if not files:
                files = self.fs_manager.list_files()
                
            if not files:
                print("⚠️ No files found in Code directory")
                return False
                
            # Review each file
            improvements_needed = False
            for file_path in files:
                is_improved = self.review_file(file_path, brain, config)
                improvements_needed = improvements_needed or is_improved
                
            if not improvements_needed:
                print("\n✅ Code review passed: No improvements needed")
                
            return True
            
        except Exception as e:
            print(f"❌ Error scanning directory: {e}")
            return False
            
    def review_file(self, file_path: Path, brain: Any, config: Dict[str, Any]) -> bool:
        """Review a single file and apply improvements if needed"""
        try:
            # Check if file exists and is supported
            if not self._is_reviewable(file_path):
                print(f"⚠️ Skipping review for {file_path} (not reviewable)")
                return False
                
            # Get file content
            content = self.fs_manager.get_file_content(file_path)
            if not content:
                print(f"⚠️ Unable to read content of {file_path}")
                return False
                
            # Generate review prompt with improved format
            file_type = file_path.suffix.lstrip('.')
            relative_path = file_path.relative_to(self.fs_manager.base_dir)  # Use base_dir instead of code_dir
            prompt = DeveloperPrompts.generate_review_prompt(
                str(relative_path),
                file_type,
                content
            )
            
            # Get feedback from LLM
            print(f"\n🔍 Reviewing: {relative_path}")
            feedback = brain.generate(prompt, config)
            
            # Check if improvements are needed
            if "VALIDATION_PASSED" in feedback:
                print(f"✅ No improvements needed for {relative_path}")
                return False
                
            # Debug the received feedback
            print(f"\n🔍 DEBUG: Review feedback received ({len(feedback)} chars)")
            print(f"Feedback preview: {feedback[:200]}...\n")
            
            # Process feedback to create/update files
            try:
                print(f"🔄 Applying suggested improvements...")
                updated_files = self.fs_manager.process_content(
                    feedback,
                    brain=brain,
                    config=config,
                    retry_prompt=prompt
                )
                
                if updated_files:
                    print(f"✅ Applied improvements to {len(updated_files)} files")
                    return True
                    
                print(f"⚠️ No valid improvements found for {relative_path}")
                return False
                
            except Exception as e:
                print(f"⚠️ Failed to process improvements: {e}")
                # Try to directly extract any code blocks
                print("🔄 Attempting alternative processing...")
                # Fallback: At least try to update the current file
                self._apply_fallback_improvement(file_path, feedback, relative_path)
                return True
            
        except Exception as e:
            print(f"❌ Error reviewing file {file_path}: {e}")
            return False
            
    def _apply_fallback_improvement(self, file_path: Path, feedback: str, relative_path: str) -> bool:
        """Fallback method to extract and apply improvements when regular parsing fails"""
        try:
            # Look for code blocks
            import re
            code_blocks = re.findall(r'```[a-zA-Z]*\n(.*?)```', feedback, re.DOTALL)
            
            if code_blocks:
                # Use the largest code block
                largest_block = max(code_blocks, key=len)
                
                # Create file info
                file_info = {
                    "path": str(relative_path),
                    "content": largest_block,
                    "description": "Applied improvements using fallback extraction",
                    "modifications": True
                }
                
                # Update file directly
                updated_path = self.fs_manager.create_or_update_file(file_info)
                if updated_path:
                    print(f"✅ Applied improvements using fallback method to {relative_path}")
                    return True
            
            print("⚠️ Could not extract improvements even with fallback method")
            return False
            
        except Exception as e:
            print(f"❌ Error in fallback improvement: {e}")
            return False
            
    def _is_reviewable(self, file_path: Path) -> bool:
        """Check if file is suitable for review"""
        # Skip directories, hidden files, and backup files
        if not file_path.is_file() or file_path.name.startswith('.'):
            return False
            
        # Skip backup files
        if file_path.name.endswith('.bak') or 'backup' in str(file_path):
            return False
            
        # List of supported file extensions for review
        supported_extensions = [
            '.py', '.js', '.ts', '.html', '.css', '.scss',
            '.jsx', '.tsx', '.json', '.yaml', '.yml', '.md',
            '.c', '.cpp', '.h', '.java', '.php', '.rb', '.go'
        ]
        
        return file_path.suffix.lower() in supported_extensions
