from typing import Dict, Any, List, Optional
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager
from Core.content_parser import ContentParser
from .prompts import TestingPrompts

class TestGenerator:
    def __init__(self):
        self.fs_manager = FileSystemManager()
        self.content_parser = ContentParser()

    def generate_tests(self, 
                      implementation_files: List[Path], 
                      technical_docs: Dict[str, str],
                      brain: Any, 
                      config: Dict) -> List[Path]:
        """Generate test files based on implementation and documentation"""
        generated_files = []
        
        for file_path in implementation_files:
            print(f"\n🔍 Analyzing {file_path} for test generation")
            
            # Get file content
            content = self.fs_manager.get_file_content(file_path)
            if not content:
                continue

            # Determine appropriate test types
            test_types = self._determine_test_types(file_path, content, technical_docs)
            
            # Generate test analysis
            analysis_prompt = TestingPrompts.analyze_for_tests(
                str(file_path),
                content,
                test_types
            )
            analysis_result = brain.generate(analysis_prompt, config)
            
            if analysis_result:
                # Parse FILE: sections from response
                test_files = self.content_parser.parse_files_section(analysis_result)
                
                # Create test files
                for file_info in test_files:
                    if path := self.fs_manager.create_or_update_file(file_info):
                        generated_files.append(path)
                        print(f"✅ Created test file: {path}")
            
        return generated_files

    def analyze_file(self, file_path: Path, brain: Any, config: Dict) -> Optional[Dict]:
        """Analyze a file and determine which tests should be created"""
        try:
            print(f"\n🔍 Analyzing {file_path.name} for test creation")
            
            content = self.fs_manager.get_file_content(file_path)
            if not content:
                return None
            
            # Get test types from config or determine automatically
            test_types = config.get('test_types', self._determine_test_types(file_path, content, {}))
            
            # Generate analysis prompt
            prompt = TestingPrompts.analyze_for_tests(
                str(file_path),
                content,
                test_types
            )
            
            # Get analysis result
            result = brain.generate(prompt, config)
            if not result:
                return None

            # Parse FILE: sections using ContentParser
            test_files = self.content_parser.parse_files_section(result)
            if test_files:
                return {"test_files": test_files}
            
            print(f"⚠️ No tests needed for {file_path.name}")
            return None
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path.name}: {e}")
            return None

    def _determine_test_types(self, 
                            file_path: Path, 
                            content: str, 
                            docs: Dict[str, str]) -> List[str]:
        """Determine which types of tests are appropriate"""
        test_types = ["unit"]  # Always include unit tests
        
        # Add test types based on file type and content
        if any(kw in content.lower() for kw in ["api", "endpoint", "router", "controller"]):
            test_types.append("integration")
            
        if "component" in str(file_path).lower() or any(kw in content.lower() for kw in ["react", "vue", "component"]):
            test_types.append("component")
            
        if docs:
            # Check docs for additional test requirements
            for doc_content in docs.values():
                if "end-to-end" in doc_content.lower() or "e2e" in doc_content.lower():
                    test_types.append("e2e")
                if "performance" in doc_content.lower():
                    test_types.append("performance")
                    
        return list(set(test_types))  # Remove duplicates

    def _create_test_files(self, implementation: str) -> List[Path]:
        """Create test files from implementation"""
        try:
            files_info = self._parse_implementation(implementation)
            created_files = []
            
            for file_info in files_info:
                if path := self.fs_manager.create_or_update_file(file_info):
                    created_files.append(path)
                    
            return created_files
        except Exception as e:
            print(f"❌ Error creating test files: {e}")
            return []

    def _parse_implementation(self, implementation: str) -> List[Dict]:
        """Parse implementation into file info dictionaries"""
        # Implementation of parsing logic here
        pass

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
            
            if not result:
                print("❌ No test implementation generated")
                return []

            # Parse FILE: sections using ContentParser
            files_info = self.content_parser.parse_files_section(result)
            if not files_info:
                print("❌ No valid test files found in response")
                return []
            
            # Process each test file
            for file_info in files_info:
                # Create the test file
                if path := self.fs_manager.create_or_update_file(file_info):
                    created_files.append(path)
                    print(f"✅ Created test file: {path}")
                else:
                    print(f"❌ Failed to create test file: {file_info.get('path', 'unknown')}")
                    
            return created_files
            
        except Exception as e:
            print(f"❌ Error creating tests: {e}")
            return []
