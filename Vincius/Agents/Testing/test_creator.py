from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
from ...Core.file_system_manager import FileSystemManager
from .prompts import TestingPrompts

class TestCreator:
    def __init__(self):
        self.fs_manager = FileSystemManager()

    def create_tests(self, source_file: Path, test_specs: Dict, brain: Any, config: Dict) -> List[Path]:
        """Create test files based on specifications"""
        try:
            created_files = []
            
            # Generate test implementation
            prompt = TestingPrompts.create_test_implementation(
                source_file.name,
                test_specs,
                config.get('guidelines', [])
            )
            result = brain.generate(prompt, config)
            
            # Extract and validate YAML
            yaml_content = self._extract_yaml(result)
            if not yaml_content:
                return []
                
            try:
                files_config = yaml.safe_load(yaml_content)
                if not files_config or "files" not in files_config:
                    return []
                    
                # Process each test file
                for file_info in files_config["files"]:
                    # Let the model decide the full path structure
                    if path := self.fs_manager.create_or_update_file(file_info):
                        created_files.append(path)
                        
            except yaml.YAMLError as e:
                print(f"❌ Error parsing test implementation: {e}")
                
            return created_files
            
        except Exception as e:
            print(f"❌ Error creating tests: {e}")
            return []

    def _extract_yaml(self, text: str) -> Optional[str]:
        """Extract YAML content from response"""
        try:
            if "files:" not in text:
                return None
                
            yaml_text = text[text.find("files:"):]
            lines = []
            inside_content = False
            content_indent = 0
            
            for line in yaml_text.splitlines():
                stripped = line.strip()
                
                # Handle content blocks
                if "content: |" in line:
                    inside_content = True
                    content_indent = len(line) - len(line.lstrip())
                    lines.append(line)
                    continue
                    
                if inside_content:
                    if not line.strip() or len(line) - len(line.lstrip()) <= content_indent:
                        inside_content = False
                    else:
                        lines.append(line)
                        continue
                        
                if stripped and not any(marker in stripped for marker in ["```", "---", "==="]):
                    lines.append(line)
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"❌ Error extracting YAML: {e}")
            return None
