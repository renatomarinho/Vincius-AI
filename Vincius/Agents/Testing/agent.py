from typing import Dict, Any, List, Optional
from pathlib import Path
from Vincius.Core.brain_model import BrainModel
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.Testing.test_generator import TestGenerator
from Vincius.Agents.Testing.test_runner import TestRunner
from Vincius.Agents.Testing.prompts import TestingPrompts

class TesterAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.brain = BrainModel()
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner()
        self.fs_manager = FileSystemManager()

    def execute(self, input_data: Any = None) -> str:
        try:
            print("\n🧪 Starting test analysis and generation...")
            
            # 1. Analyze technical documentation
            docs = self._read_technical_docs()
            if not docs:
                print("⚠️ No technical documentation found, proceeding with file analysis only")
            
            # 2. Find all implementation files
            implementation_files = self._find_implementation_files()
            if not implementation_files:
                return "❌ No implementation files found to test"
            
            print(f"\n📁 Found {len(implementation_files)} files to analyze for testing")
            
            # 3. Generate and create tests
            test_files = self.test_generator.generate_tests(
                implementation_files=implementation_files,
                technical_docs=docs,
                brain=self.brain,
                config=self.config
            )
            
            if not test_files:
                return "❌ Failed to generate tests"
            
            print(f"\n✅ Generated {len(test_files)} test files")
            return f"Successfully created {len(test_files)} test files"
            
        except Exception as e:
            print(f"\n❌ Error in testing process: {e}")
            return f"Error executing agent: {str(e)}"

    def _read_technical_docs(self) -> Dict[str, str]:
        """Read all technical documentation from docs folder"""
        docs = {}
        try:
            docs_path = self.fs_manager.code_dir / "docs"
            if not docs_path.exists():
                return {}

            for file in docs_path.glob("*.md"):
                content = self.fs_manager.get_file_content(file.relative_to(self.fs_manager.code_dir))
                if content:
                    docs[file.name] = content

            if docs:
                print(f"\n📚 Found {len(docs)} technical documentation files")
            
            return docs
        except Exception as e:
            print(f"⚠️ Error reading documentation: {e}")
            return {}

    def _find_implementation_files(self) -> List[Path]:
        """Find all files that need tests using AI analysis"""
        try:
            # Get all files recursively (excluding hidden and special directories)
            all_files = [
                f.relative_to(self.fs_manager.code_dir) 
                for f in self.fs_manager.code_dir.rglob('*')
                if f.is_file() and not any(part.startswith(('.', '__')) for part in f.parts)
            ]
            
            if not all_files:
                return []

            # Ask model which files need tests
            files_content = "\n".join(f"- {f}" for f in sorted(all_files))
            prompt = TestingPrompts.analyze_files_for_testing(files_content)
            
            response = self.brain.generate(prompt, self.config)
            if not response:
                return []

            # Parse response to get files that need testing
            files_to_test = []
            for file in all_files:
                file_str = str(file)
                if file_str in response:
                    # Get the reason if provided
                    reason = self._extract_reason(response, file_str)
                    if reason:
                        print(f"✅ File needs tests: {file_str}")
                        print(f"   Reason: {reason}")
                    files_to_test.append(file)

            return sorted(files_to_test)
            
        except Exception as e:
            print(f"⚠️ Error finding implementation files: {e}")
            return []

    def _extract_reason(self, response: str, file_path: str) -> Optional[str]:
        """Extract reason why file needs tests from model response"""
        try:
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if file_path in line:
                    # Try to get the next line as reason if it starts with a reason indicator
                    if i + 1 < len(lines) and any(lines[i + 1].strip().startswith(x) for x in ['- ', '• ', '* ', 'Reason:']):
                        return lines[i + 1].strip().lstrip('- •*').replace('Reason:', '').strip()
            return None
        except Exception:
            return None
