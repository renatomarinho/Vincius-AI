import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil
from datetime import datetime
import re
import yaml
from Vincius.Core.content_parser import ContentParser
from Vincius.Core.config_manager import ConfigManager
from Vincius.Core.developer_logger import DeveloperLogger
from Vincius.Core.analyst_logger import AnalystLogger
from Vincius.Core.logger_base import LoggerBase
from importlib import import_module

class FileSystemManager:
    """Manages file system operations for code generation and modifications"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.content_parser = ContentParser()
        self.project_root = self.config_manager.base_path
        
        # Initialize logger based on current agent type
        self.current_agent = os.environ.get('CURRENT_AGENT_TYPE', 'Developer')
        self.agent_config = self._get_agent_config()
        
        # Create and initialize base directory
        self.base_dir = self._initialize_base_directory()
        self.logger = self._initialize_logger()
        
        print(f"🔧 Initialized {self.current_agent} agent in {self.base_dir}")

    def _get_agent_config(self) -> Dict:
        """Get agent configuration from workflow"""
        try:
            workflow = self.config_manager.get_workflow()
            for step in workflow['workflow'].values():
                if step['action']['class'].replace('Agent', '') == self.current_agent:
                    return step['action']['agent_config']
            raise ValueError(f"Configuration not found for agent: {self.current_agent}")
        except Exception as e:
            raise ValueError(f"Failed to get agent configuration: {e}")

    def _initialize_base_directory(self) -> Path:
        """Initialize and verify base directory for agent"""
        base_dir_key = self.agent_config.get('base_dir_key')
        if not base_dir_key:
            raise ValueError(f"base_dir_key not defined for agent {self.current_agent} in workflow configuration")
        
        base_dir = self.project_root / base_dir_key
        os.makedirs(base_dir, exist_ok=True)
        
        if not base_dir.exists():
            raise IOError(f"Failed to create/verify directory: {base_dir}")
            
        return base_dir

    def _initialize_logger(self) -> LoggerBase:
        """Initialize appropriate logger for agent"""
        logger_class = self._get_logger_class()
        return logger_class(self.project_root)

    def _get_logger_class(self) -> type:
        """Get logger class dynamically based on agent type"""
        try:
            # Import logger dynamically
            module_name = f"Vincius.Core.{self.current_agent.lower()}_logger"
            class_name = f"{self.current_agent}Logger"
            
            module = import_module(module_name)
            logger_class = getattr(module, class_name)
            
            return logger_class
        except Exception as e:
            raise ValueError(f"Failed to load logger for agent {self.current_agent}: {e}")

    def _clean_path(self, path: str) -> str:
        """Clean path from invalid characters and decorations"""
        # Remove asterisks and other special characters
        clean = re.sub(r'[*]+$', '', path)  # Remove trailing asterisks
        clean = re.sub(r'\s+', '', clean)   # Remove whitespace
        clean = clean.replace('\\', '/')     # Normalize slashes
        return clean.strip()

    def create_or_update_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """Create or update a file with its directory structure"""
        try:
            if not isinstance(file_info, dict) or 'path' not in file_info or 'content' not in file_info:
                print("⚠️ Invalid file info structure")
                return None

            path = file_info["path"]
            content = self.content_parser.clean_code_block(file_info['content'])  # Usa o content_parser para limpar o conteúdo antes de salvar
            is_modification = file_info.get("modifications", False)
            description = file_info.get("description", "")

            if not content:
                print(f"⚠️ No content provided for {path}")
                return None

            # Always use absolute paths and verify directory
            file_path = Path(str(path))

            # Use the agent's base directory
            if not file_path.is_absolute():
                full_path = self.base_dir / file_path
            else:
                try:
                    rel_path = file_path.relative_to(self.base_dir)
                    full_path = self.base_dir / rel_path
                except ValueError:
                    full_path = file_path

            print(f"\n📝 File operation details:")
            print(f"Path: {file_path}")
            print(f"Full path: {full_path}")
            print(f"Absolute path: {full_path.absolute()}")
            print(f"Operation: {'Modifying' if is_modification else 'Creating'}")
            if description:
                print(f"Description: {description}")

            # Create directory structure with explicit error checking
            try:
                os.makedirs(full_path.parent, exist_ok=True)
                if not full_path.parent.exists():
                    raise IOError(f"Failed to create directory: {full_path.parent}")
                print(f"📁 Created/Verified directory: {full_path.parent}")
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")
                raise

            # Backup if modifying existing file
            if is_modification and full_path.exists():
                backup_path = self.backup_file(full_path)
                print(f"💾 Backup created: {backup_path.name}")

            # Write file content with explicit verification
            try:
                with open(full_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                
                # Verify file was created and content was written
                if not full_path.exists():
                    raise FileNotFoundError(f"File was not created: {full_path}")
                
                written_content = full_path.read_text(encoding='utf-8')
                if not written_content:
                    raise IOError(f"File was created but content is empty: {full_path}")
                
                print(f"✅ File written successfully: {full_path}")
                print(f"✅ Content length: {len(written_content)} characters")
                
                # Log using the current agent's logger
                self.logger.log_file_creation(
                    full_path,
                    description=file_info.get("description", ""),
                    is_modification=file_info.get("modifications", False),
                    content=content
                )
                print(f"📝 Logged by {self.current_agent} agent")
                return full_path

            except Exception as e:
                print(f"❌ Failed to write file: {e}")
                print(f"Directory exists: {full_path.parent.exists()}")
                print(f"Is directory writable: {os.access(full_path.parent, os.W_OK)}")
                print(f"Current permissions: {oct(os.stat(full_path.parent).st_mode)[-3:]}")
                raise

        except Exception as e:
            print(f"❌ Error processing file: {e}")
            print(f"Stack trace:")
            import traceback
            print(traceback.format_exc())
            return None

    def process_content(self, content: str, brain: Any = None, config: Dict = None, retry_prompt: str = None) -> List[Path]:
        """Process content in text format and create files"""
        print("\n🔍 DEBUG: File System Manager - Process Content Start")
        print("=" * 50)
        print(f"Content length: {len(content)} characters")
        print(f"Content preview:\n{content[:200]}...")
        
        # Create a ContentParser instance to use non-static methods
        parser = ContentParser()
        
        processed_files = []
        max_retries = 3
        current_try = 0
        
        while current_try < max_retries:
            try:
                print(f"\n📝 DEBUG: Parsing attempt {current_try + 1}")
                
                # Use the improved parsing methods
                files_info = parser.parse_files_section(content)
                
                if not files_info:
                    # Try even more aggressive parsing for file sections
                    print("⚠️ Standard parsing failed, trying emergency parsing...")
                    files_info = self._emergency_parse_files(content)
                
                if not files_info:
                    print("⚠️ DEBUG: No valid file sections found in content")
                    print("Content structure might not match expected format")
                    raise ValueError("No valid file sections found")

                print(f"\n🔄 DEBUG: Processing {len(files_info)} files...")
                
                for file_info in files_info:
                    print(f"\n📄 DEBUG: Processing file: {file_info.get('path', 'unknown')}")
                    if path := self.create_or_update_file(file_info):
                        print(f"✅ DEBUG: Successfully created: {path}")
                        processed_files.append(path)
                    else:
                        print(f"❌ DEBUG: Failed to create file")

                if processed_files:
                    print(f"\n✅ DEBUG: Successfully processed files:")
                    for path in processed_files:
                        print(f"- {path}")
                        # Verify file exists and has content
                        if path.exists():
                            content_length = len(path.read_text(encoding='utf-8'))
                            print(f"  Content length: {content_length} chars")
                        else:
                            print(f"  ⚠️ File does not exist!")
                    return processed_files
                    
                raise ValueError("No files were processed successfully")

            except Exception as e:
                current_try += 1
                print(f"\n⚠️ DEBUG: Attempt {current_try} failed: {str(e)}")
                print(f"Stack trace:")
                import traceback
                print(traceback.format_exc())
                
                if brain and config and retry_prompt and current_try < max_retries:
                    print("\n🔄 DEBUG: Requesting new implementation...")
                    content = brain.generate(retry_prompt, config)
                else:
                    print("❌ DEBUG: No retry possible")

        print("\n❌ DEBUG: All attempts failed")
        return processed_files

    def _emergency_parse_files(self, content: str) -> List[Dict[str, Any]]:
        """Last resort parsing for file sections when all else fails"""
        files = []
        
        # Simple regex to find file names and extensions
        file_patterns = [
            r'([\w\-\.\/]+\.(html|css|js|py|md|json|xml|txt))',  # Common extensions
            r'FILE:\s*([\w\-\.\/]+\.[a-zA-Z0-9]+)',  # FILE: pattern
            r'Path:\s*([\w\-\.\/]+\.[a-zA-Z0-9]+)'   # Path: pattern
        ]
        
        # Find all potential filenames
        potential_files = set()
        for pattern in file_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                filename = match.group(1).strip() if len(match.groups()) > 0 else ""
                if filename:
                    potential_files.add(filename)
        
        # For each potential filename, try to extract content
        for filename in potential_files:
            # Find the position of the filename
            pos = content.find(filename)
            if pos >= 0:
                # Extract everything after the filename until next potential filename or end
                next_pos = len(content)
                for next_file in potential_files:
                    if next_file != filename:
                        next_file_pos = content.find(next_file, pos + len(filename))
                        if next_file_pos > pos and next_file_pos < next_pos:
                            next_pos = next_file_pos
                
                # Extract the content
                file_section = content[pos:next_pos].strip()
                
                # Try to find where the actual content starts
                content_start = file_section.find('\n')
                if content_start > 0:
                    file_content = file_section[content_start:].strip()
                    
                    # Clean up the content - remove common prefixes
                    file_content = re.sub(r'^Content:[\s]*\n', '', file_content, flags=re.IGNORECASE)
                    
                    files.append({
                        "path": filename,
                        "content": file_content,
                        "description": f"Extracted using emergency parsing",
                        "modifications": False
                    })
        
        if files:
            print(f"✅ Found {len(files)} file sections using emergency parsing")
            
        return files

    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of a file with timestamp"""
        backup_dir = self.base_dir / "backups"  # Use base_dir instead of code_dir
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
        backup_path = backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path

    def get_file_content(self, file_path: Path) -> Optional[str]:
        """Safely read file content"""
        try:
            full_path = self.base_dir / file_path  # Use base_dir instead of code_dir
            if not full_path.exists():
                print(f"⚠️ File not found: {file_path}")
                return None
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None

    def verify_structure(self, files: List[Path], brain: Any, config: Dict) -> bool:
        """Verify project structure and create missing files if needed"""
        try:
            structure = self._create_structure_representation(files)
            print("\n🔍 Verifying project structure...")
            
            if not files:
                print("⚠️ No files to verify")
                return False

            print("\nCurrent structure:")
            print(structure)
            return True
            
        except Exception as e:
            print(f"❌ Error verifying structure: {e}")
            return False

    def _create_structure_representation(self, files: List[Path]) -> str:
        """Create a string representation of the file structure"""
        try:
            sorted_files = sorted(files, key=lambda x: str(x.relative_to(self.base_dir)))  # Use base_dir
            structure = []
            
            for file_path in sorted_files:
                rel_path = file_path.relative_to(self.base_dir)  # Use base_dir
                structure.append(f"- {rel_path}")
            
            return "\n".join(structure)
        except Exception as e:
            print(f"❌ Error creating structure representation: {e}")
            return ""

    def list_files(self, directory: Optional[str] = None) -> List[Path]:
        """List all files in directory"""
        try:
            search_dir = self.base_dir  # Use base_dir instead of code_dir
            if directory:
                search_dir = search_dir / directory
            
            if not search_dir.exists():
                print(f"⚠️ Directory not found: {directory}")
                return []

            files = list(search_dir.rglob('*'))
            return [f for f in files if f.is_file()]
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []

    def delete_file(self, file_path: Path, backup: bool = True) -> bool:
        """Safely delete a file with optional backup"""
        try:
            full_path = self.base_dir / file_path  # Use base_dir instead of code_dir
            if not full_path.exists():
                print(f"⚠️ File not found: {file_path}")
                return False

            if backup:
                self.backup_file(full_path)
                print(f"💾 Backup created before deletion")

            full_path.unlink()
            print(f"🗑️ Deleted: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")
            return False
