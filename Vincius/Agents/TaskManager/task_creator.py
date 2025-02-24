from typing import Dict, Any, Optional, List
import csv
from io import StringIO
from pathlib import Path
from Vincius.Core.file_system_manager import FileSystemManager
from Vincius.Core.content_parser import ContentParser
from Vincius.Agents.TaskManager.prompts import TaskManagerPrompts

class TaskCreator:
    EXPECTED_COLUMNS = ['id', 'title', 'description', 'task_type', 'difficulty']
    VALID_TYPES = ['Feature', 'Bug', 'Enhancement', 'Documentation', 'Testing']
    VALID_DIFFICULTIES = ['Easy', 'Medium', 'Hard']

    def __init__(self):
        self.fs_manager = FileSystemManager()
        self.content_parser = ContentParser()

    def create_project_tasks(self, analysis_result: str, brain: Any, config: Dict) -> Optional[str]:
        """Create project tasks based on technical analysis"""
        try:
            print("\n📊 Generating task breakdown in CSV format...")
            
            # Generate tasks directly in CSV format
            prompt = TaskManagerPrompts.create_tasks_csv(analysis_result)  # Corrigido aqui
            result = brain.generate(prompt, config)
            
            if not result:
                print("❌ Failed to generate tasks")
                return None

            # Parse FILE: sections from response
            files_info = self.content_parser.parse_files_section(result)
            if not files_info:
                print("❌ No valid task list found in response")
                return None

            # Save CSV file
            for file_info in files_info:
                if file_info.get('path', '').endswith('.csv'):
                    # Validate and clean CSV content
                    cleaned_content = self._validate_and_clean_csv(file_info['content'])
                    if not cleaned_content:
                        print("❌ Invalid CSV format")
                        continue

                    file_info['content'] = cleaned_content
                    if path := self.fs_manager.create_or_update_file(file_info):
                        print(f"✅ Task list saved at: {path}")
                        return file_info['content']
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating task list: {e}")
            return None

    def _validate_and_clean_csv(self, content: str) -> Optional[str]:
        """Validate and clean CSV content to ensure proper format"""
        try:
            # Read CSV content
            lines = content.strip().split('\n')
            if len(lines) < 2:
                print("❌ CSV must have header and at least one task")
                return None

            # Parse CSV using StringIO to handle newlines in fields
            rows = []
            reader = csv.reader(StringIO(content), quotechar='"', delimiter=',')
            for row in reader:
                rows.append(row)

            # Validate header
            header = [col.strip().lower() for col in rows[0]]
            if not all(col in header for col in self.EXPECTED_COLUMNS):
                print("❌ CSV header missing required columns")
                print(f"Expected: {self.EXPECTED_COLUMNS}")
                print(f"Got: {header}")
                return None

            # Clean and validate each row
            cleaned_rows = [self.EXPECTED_COLUMNS]  # Start with header
            for row in rows[1:]:
                # Ensure correct number of columns
                if len(row) != len(self.EXPECTED_COLUMNS):
                    # Fix row by truncating or padding
                    row = row[:len(self.EXPECTED_COLUMNS)] if len(row) > len(self.EXPECTED_COLUMNS) else row + [''] * (len(self.EXPECTED_COLUMNS) - len(row))
                
                # Clean each field
                cleaned_row = []
                for i, field in enumerate(row):
                    # Clean field based on column type
                    clean_field = self._clean_field(field.strip(), self.EXPECTED_COLUMNS[i])
                    cleaned_row.append(clean_field)
                
                cleaned_rows.append(cleaned_row)

            # Convert back to CSV string
            output = StringIO()
            writer = csv.writer(output, quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerows(cleaned_rows)
            
            return output.getvalue()

        except Exception as e:
            print(f"❌ Error validating CSV: {e}")
            return None

    def _clean_field(self, field: str, column: str) -> str:
        """Clean field based on column type"""
        if not field:
            # Default values for empty fields
            defaults = {
                'id': 'T000',
                'task_type': 'Feature',
                'difficulty': 'Medium'
            }
            return defaults.get(column, '')

        if column == 'id':
            # Ensure proper ID format (T001, T002, etc)
            if not field.startswith('T'):
                field = 'T' + field
            number = ''.join(filter(str.isdigit, field))
            return f"T{int(number or 0):03d}"

        if column == 'task_type':
            # Normalize task type
            normalized = field.strip().title()
            return normalized if normalized in self.VALID_TYPES else 'Feature'

        if column == 'difficulty':
            # Normalize difficulty
            normalized = field.strip().title()
            return normalized if normalized in self.VALID_DIFFICULTIES else 'Medium'

        return field.strip()

    def review_tasks(self, tasks: str, brain: Any, config: Dict) -> bool:
        """Verify task list is complete and well-formed"""
        try:
            lines = tasks.strip().split('\n')
            if len(lines) < 2:  # Header + at least one task
                return False
                
            header = lines[0].lower()
            required_columns = ['task_id', 'task_name', 'phase', 'description', 'dependencies']
            
            return all(col in header for col in required_columns)
            
        except Exception as e:
            print(f"❌ Error reviewing tasks: {e}")
            return False
