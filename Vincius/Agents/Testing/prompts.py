from typing import Dict, List

class TestingPrompts:
    @staticmethod
    def analyze_for_tests(file_name: str, content: str, test_types: List[str]) -> str:
        return f"""
You are a senior test engineer. Analyze this file and determine appropriate test cases.
Consider implementing these test types: {', '.join(test_types)}

File: {file_name}
Content:
{content}

Based on the file type and content, determine:
1. Appropriate test framework and methodology
2. Test naming conventions for this framework
3. Required test structure and organization
4. Necessary test cases for each type

For each test type, provide your analysis using this format:

FILE: tests/{file_name}
Type: test
Description: |
  Framework: [Test framework name and version]
  Naming Convention: [Explain test naming convention]
  Structure: [Explain test organization]
  
Content:
[Complete test implementation including:
- Imports and setup
- Test cases with descriptions
- Assertions and verifications
- Proper test organization]

You can specify multiple test files if needed. Follow the framework's best practices.
"""

    @staticmethod
    def create_test_implementation(file_name: str, test_specs: Dict, guidelines: List[str]) -> str:
        guidelines_text = "\n".join(f"- {g}" for g in guidelines)
        
        return f"""
You are a senior test engineer implementing tests based on the previous analysis.
Create the appropriate test files following the framework's best practices.

Source File: {file_name}
Test Specifications:
{test_specs}

Guidelines to follow:
{guidelines_text}

Provide implementation using this format:

FILE: [path/to/test_file]
Type: test
Description: |
  Framework choice and organization details
Content:
[Complete test implementation]

You can create multiple test files. Make sure to:
1. Follow the chosen framework's conventions
2. Use proper file naming and organization
3. Implement all specified test cases
4. Include necessary configuration files
5. Add appropriate documentation
6. Handle all dependencies correctly
"""

    @staticmethod
    def analyze_files_for_testing(files_list: str) -> str:
        return f"""
As a senior test engineer, analyze this list of files and determine which ones need automated tests.
Consider file types, naming patterns, and typical testing requirements.

Files to analyze:
{files_list}

For each file that needs tests, explain why. Consider:
1. Is it source code that implements business logic?
2. Does it contain critical functionality?
3. Is it a type of file that typically requires testing (e.g. controllers, services, utils)?
4. Would testing this file improve system reliability?

Respond with a list of files that need tests and brief explanation for each:

[filepath]
Reason: [Brief explanation why this file needs tests]

[filepath]
Reason: [Brief explanation why this file needs tests]

Only include files that genuinely need automated tests.
"""

    @staticmethod
    def test_generation(implementation: str) -> str:
        """Generate prompt for test creation"""
        pass

    @staticmethod
    def test_result_analysis(test_results: str) -> str:
        """Generate prompt for analyzing test results"""
        pass