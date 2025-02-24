class AnalystPrompts:
    @staticmethod
    def requirements_analysis(requirements: str, base_prompt: str = "") -> str:
        return f"""
As a senior systems analyst,
analyze these requirements and provide a comprehensive technical analysis.

Requirements:
{requirements}

{base_prompt}

Provide your analysis using the following structure:

OVERVIEW:
[General system description]

COMPONENTS:
- Name: [Component Name]
  Description: [Purpose and functionality]
  Requirements:
  - [Required specifications]
  - [Dependencies]

TECHNICAL SPECIFICATIONS:
- Architecture:
  [Architecture description]
- Technologies:
  [Required technologies]
- Security:
  [Security requirements]
- Performance:
  [Performance requirements]
- Scalability:
  [Scalability requirements]

IMPLEMENTATION DETAILS:
- Phase: [Phase Name]
  Details: [Implementation specifics]
  Requirements:
  - [Technical requirements]
  - [Best practices]

If the analysis is ready, respond with:
"VALIDATION_PASSED: Analysis contains all necessary technical details for implementation."
"""

    @staticmethod
    def review_analysis(analysis: str) -> str:
        return f"""
Review this technical analysis for completeness and accuracy.

Analysis Content:
{analysis}

Verify these aspects are defined:

1. Core Components
2. Technical Requirements
3. Implementation Guidelines
4. Technical Constraints

If improvements needed, respond with:
IMPROVEMENTS NEEDED:
[List specific improvements required]

If the analysis is ready, respond with:
"VALIDATION_PASSED: Analysis contains all necessary technical details for implementation."
"""

    @staticmethod
    def final_report(analysis: str, review_result: str) -> str:
        return f"""
Generate a technical analysis report based on the provided content.

Analysis:
{analysis}

Review:
{review_result}

Required sections:
# Technical Analysis Report

## Executive Summary
## System Analysis
## Technical Specifications
## Implementation Plan
## Recommendations

If the report is ready, respond with:
"VALIDATION_PASSED: Report contains all necessary details and is properly formatted."
"""

    @staticmethod
    def request_improvements(missing_sections: list) -> str:
        sections_list = "\n".join(f"- {section}" for section in missing_sections)
        return f"""
Enhance the analysis with these missing sections:

{sections_list}

For each section provide:
- Technical specifications
- Requirements
- Considerations
- Best practices

If complete, respond with:
"VALIDATION_PASSED: All requested sections have been detailed."
"""

    @staticmethod
    def analyze_review_feedback(feedback: str) -> str:
        return f"""
Review this feedback and suggest improvements:

{feedback}

Provide:
1. Areas needing enhancement
2. Missing details
3. Required clarifications

If complete, respond with:
"VALIDATION_PASSED: All feedback analyzed and recommendations provided."
"""
