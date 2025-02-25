from typing import Dict, List, Any

class DeveloperPrompts:
    @staticmethod
    def code_creation(input_data: str, guidelines: List[str]) -> str:
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
    @staticmethod
    def structure_verification(structure: str) -> str:
        return f"""
As a software architect, analyze if this project structure is complete.

Current structure:
{structure}

If any files are missing or need modifications, respond in YAML format:

files:
  - path: path/to/new/file  # For new files
    type: file_type
    description: "Why this file is needed"
    CONTENT_START
      [File content]
    CONTENT_END

  - path: path/to/existing/file  # For modifications
    type: file_type
    description: "Why modifications are needed"
    modifications: true
    CONTENT_START
      [Updated content]
    CONTENT_END

If structure is complete, respond with:
"Structure is complete and correct."
"""

    @staticmethod
    def code_review(file_path: str, file_type: str, content: str) -> str:
        return f"""
As a senior code reviewer, analyze this code for improvements.

File: {file_path}
Type: {file_type}

Current content:
{content}

You can:
1. Suggest improvements to the current file
2. Create new related files
3. Modify other existing files
4. Add supporting files (configs, tests, etc)

Provide your response in YAML format:

files:
  # Improvements for current file
  - path: {file_path}
    type: {file_type}
    description: |
      Explain needed improvements...
    CONTENT_START
      [Improved code]
    CONTENT_END

  # Any new files needed
  - path: path/to/new/file
    type: file_type
    description: |
      Why this new file is needed...
    CONTENT_START
      [New file content]
    CONTENT_END

  # Modifications to related files
  - path: path/to/related/file
    type: file_type
    description: |
      Why this file needs changes...
    modifications: true
    CONTENT_START
      [Updated content]
    CONTENT_END

If no improvements needed, respond with:
"VALIDATION_PASSED: Code follows all best practices."
"""

    @staticmethod
    def request_complete_file(file_path: str, partial_content: str) -> str:
        return f"""
This file appears incomplete. Please provide the complete implementation.
Keep any existing code intact and complete the implementation.

File: {file_path}
Partial Content:
{partial_content}

Provide complete implementation using this format:

FILE: {file_path}
Type: {file_path.split('.')[-1]}
Description: Complete implementation
CONTENT_START
[Complete file content here]
CONTENT_END
"""

    @staticmethod
    def request_refactoring(file_path: str, content: str, max_lines: int) -> str:
        return f"""
This file is too large (over {max_lines} lines). Please refactor it into smaller, logically separated files.
Follow SOLID principles and maintain clean architecture.

Original File: {file_path}
Current Content:
{content}

Please refactor into multiple files using this format for each new file:

FILE: [path/to/new/file.ext]
Type: [file_type]
Description: Explain what this component does and why it was separated
CONTENT_START
[Complete implementation]
CONTENT_END

Guidelines:
1. Each file should be under {max_lines} lines
2. Follow single responsibility principle
3. Maintain logical separation of concerns
4. Include necessary imports
5. Update class/function references
6. Ensure all files are complete and functional
7. Keep related functionality together
8. Add clear documentation
"""

    @staticmethod
    def generate_review_prompt(file_path: str, file_type: str, content: str) -> str:
        """Generate more explicit review prompt with proper file format"""
        return f"""
As a senior code reviewer, analyze this code for improvements.

File: {file_path}
Type: {file_type}

Current content:
{content}

You must respond in a specific format:

If you find issues that need improvements, respond with:

FILE: {file_path}
Description: [Explain what issues were found and what improvements are being made]
Content:
[Complete improved version of the file]

You can suggest additional files if needed using the same format:

FILE: [new-file-path]
Description: [Why this new file is needed]
Content:
[Complete file content]

If no improvements are needed, respond exactly with:
"VALIDATION_PASSED: Code follows best practices. No improvements needed."

Remember to maintain proper indentation and formatting in your code examples.
"""