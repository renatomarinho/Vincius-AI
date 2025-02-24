from typing import Dict, Any, List, Optional
from pathlib import Path
import re
import ast
import os
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Core.content_parser import ContentParser
from Vincius.Agents.Developer.prompts import DeveloperPrompts

class CodeReviewer:
    MAX_FILE_LINES = 500

    def __init__(self):
        self.fs_manager = FileSystemManager()
        self.content_parser = ContentParser()

    def review_files(self, files: List[Path], brain: Any, config: Dict) -> None:
        """Review and improve code files"""
        try:
            # Expand file list to include all files in Code directory
            all_files = self._get_all_files()
            if not all_files:
                print("⚠️ No files found in Code directory")
                return

            print(f"\n📂 Found {len(all_files)} files to review")
            for file_path in all_files:
                print(f"\n📋 Reviewing: {file_path}")
                
                # Read current content
                content = self.fs_manager.get_file_content(file_path)
                if not content:
                    continue

                # Check file size and completeness
                num_lines = len(content.splitlines())
                if num_lines > self.MAX_FILE_LINES:
                    print(f"⚠️ File {file_path} is too large ({num_lines} lines). Requesting refactoring...")
                    refactored_files = self._request_refactoring(file_path, content, brain, config)
                    if refactored_files:
                        print("✅ File successfully refactored into smaller components")
                        continue
                    else:
                        print("⚠️ Proceeding with review of large file...")

                if not self._is_file_complete(file_path, content):
                    print(f"⚠️ File {file_path} appears incomplete. Requesting complete version...")
                    complete_content = self._request_complete_file(file_path, content, brain, config)
                    if complete_content:
                        content = complete_content
                    else:
                        print(f"❌ Failed to get complete version of {file_path}")
                        continue
                
                # Generate and execute review
                prompt = DeveloperPrompts.generate_review_prompt(
                    str(file_path),
                    file_path.suffix[1:],
                    content
                )
                review_result = brain.generate(prompt, config)
                
                # Process review results
                if "VALIDATION_PASSED" in review_result:
                    print(f"✅ No improvements needed for {file_path.name}")
                    continue
                
                # Process improvements if needed
                self._process_improvements(review_result)
                
        except Exception as e:
            print(f"❌ Error in review_files: {e}")

    def _is_file_complete(self, file_path: Path, content: str) -> bool:
        if not content:
            return False

        # Check for obvious truncation
        if content.rstrip().endswith(('(', '{', '[', ',', '\\', '+')):
            return False

        # For Python files, try parsing the AST
        if file_path.suffix.lower() == '.py':
            try:
                ast.parse(content)
                return True
            except SyntaxError:
                return False

        # Count opening/closing brackets/braces
        brackets = {'(': ')', '{': '}', '[': ']'}
        counts = {char: 0 for chars in brackets.items() for char in chars}
        
        for char in content:
            if char in counts:
                counts[char] += 1
                
        for opener, closer in brackets.items():
            if counts[opener] != counts[closer]:
                return False

        # Check for incomplete string literals
        quote_chars = '"\'`'
        for quote in quote_chars:
            if content.count(quote) % 2 != 0:
                return False

        return True

    def _request_complete_file(self, file_path: Path, partial_content: str, brain: Any, config: Dict) -> Optional[str]:
        """Request complete version of incomplete file"""
        prompt = DeveloperPrompts.request_complete_file(file_path.name, partial_content)
        
        try:
            result = brain.generate(prompt, config)
            files_info = self.content_parser.parse_files_section(result)
            
            if not files_info:
                return None
                
            # Get first file's content
            if len(files_info) > 0 and files_info[0].get('content'):
                content = files_info[0]['content']
                if self._is_file_complete(file_path, content):
                    return content
                    
            return None
            
        except Exception as e:
            print(f"❌ Error requesting complete file: {e}")
            return None

    def _process_improvements(self, review_result: str) -> None:
        """Process improvement suggestions"""
        try:
            files_info = self.content_parser.parse_files_section(review_result)
            
            # Process each file
            for file_info in files_info:
                if self._is_file_complete(Path(file_info["path"]), file_info["content"]):
                    self.fs_manager.create_or_update_file(file_info)
                else:
                    print(f"⚠️ Skipping incomplete file: {file_info['path']}")
                    
        except Exception as e:
            print(f"❌ Error processing improvements: {e}")

    def _generate_review_prompt(self, file_path: Path, content: str) -> str:
        """Generate review prompt using DeveloperPrompts"""
        return DeveloperPrompts.generate_review_prompt(
            file_path.name,
            file_path.suffix.lstrip('.'),
            content
        )

    def _request_refactoring(self, file_path: Path, content: str, brain: Any, config: Dict) -> bool:
        """Request refactoring of large file into smaller components"""
        prompt = DeveloperPrompts.request_refactoring(
            str(file_path), 
            content, 
            self.MAX_FILE_LINES
        )
        
        try:
            result = brain.generate(prompt, config)
            files_info = self.content_parser.parse_files_section(result)
            
            if not files_info:
                return False

            # Verify all refactored files are complete and smaller
            all_valid = True
            for file_info in files_info:
                file_content = file_info.get('content', '')
                if len(file_content.splitlines()) > self.MAX_FILE_LINES:
                    print(f"⚠️ Refactored file {file_info['path']} is still too large")
                    all_valid = False
                    continue
                    
                if not self._is_file_complete(Path(file_info['path']), file_content):
                    print(f"⚠️ Refactored file {file_info['path']} is incomplete")
                    all_valid = False
                    continue
                    
                # Create the refactored file
                self.fs_manager.create_or_update_file(file_info)
                print(f"✅ Created refactored file: {file_info['path']}")

            return all_valid
            
        except Exception as e:
            print(f"❌ Error during refactoring: {e}")
            return False

    def _get_all_files(self) -> List[Path]:
        """Get all files recursively from Code directory"""
        try:
            code_dir = self.fs_manager.code_dir
            if not code_dir.exists():
                print(f"⚠️ Code directory not found at: {code_dir}")
                return []

            print(f"\n🔍 Scanning directory: {code_dir}")
            all_files = []
            
            # Walk through all directories
            for root, dirs, files in os.walk(code_dir):
                root_path = Path(root)
                
                # Skip certain directories
                dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
                
                for file in files:
                    # Skip hidden and system files
                    if file.startswith(('.', '__')):
                        continue
                        
                    file_path = root_path / file
                    rel_path = file_path.relative_to(code_dir)
                    print(f"📄 Found: {rel_path}")
                    all_files.append(rel_path)

            print(f"\n✅ Found {len(all_files)} files to review")
            return sorted(all_files)  # Sort for consistent ordering

        except Exception as e:
            print(f"❌ Error scanning directory: {e}")
            return []
