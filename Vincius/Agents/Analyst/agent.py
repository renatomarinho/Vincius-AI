from typing import Dict, Any
import logging
from Vincius.Core.brain_model import BrainModel
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Agents.Analyst.reviewer import AnalysisReviewer
from Vincius.Agents.Analyst.analyzer import RequirementsAnalyzer, AnalysisResult
from Vincius.Agents.Analyst.prompts import AnalystPrompts
from Vincius.Core.file_system_manager import FileSystemManager


class AnalystAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.brain = BrainModel()
        self.analyzer = RequirementsAnalyzer()
        self.reviewer = AnalysisReviewer()
        self.fs_manager = FileSystemManager()
        
        # Ensure docs directory exists
        (self.fs_manager.code_dir / "docs").mkdir(exist_ok=True)

    def execute(self, input_data: Any = None) -> str:
        try:
            print("\n🚀 Starting requirements analysis...")
            
            # Generate initial analysis
            result = self.analyzer.analyze_requirements(
                str(input_data),
                self.brain,
                self.config
            )
            
            if not result.structured_content:
                return "Error: No valid analysis generated"
            
            # Save technical analysis first
            technical_analysis = self._format_technical_analysis(result.content)
            tech_file_info = {
                "path": "docs/technical_requirements.md",
                "type": "markdown",
                "content": technical_analysis,
                "description": "Technical Requirements Analysis"
            }
            
            print("\n📝 Saving technical analysis...")
            tech_file = self.fs_manager.create_or_update_file(tech_file_info)
            if not tech_file:
                print("❌ Failed to save technical analysis")
                return "Error: Failed to save technical analysis"
            
            print(f"✅ Technical analysis saved at: {tech_file}")
            
            # Review and generate final report
            if self.reviewer.review_analysis(result.content, self.brain, self.config):
                print("\n📝 Generating final report...")
                final_prompt = AnalystPrompts.final_report(result.content, "Analysis Approved")
                report = self.brain.generate(final_prompt, self.config)
                
                if not report or not report.strip():
                    print("❌ No report content generated")
                    return "Error: Empty report generated"

                # Save final report
                report_file_info = {
                    "path": "docs/final_analysis.md",
                    "type": "markdown",
                    "content": report.strip(),
                    "description": "Final Analysis Report"
                }
                
                print("\n📝 Saving final report...")
                report_file = self.fs_manager.create_or_update_file(report_file_info)
                if not report_file:
                    print("❌ Failed to save final report")
                    return "Error: Failed to save final report"
                
                print(f"✅ Final report saved at: {report_file}")
                return report
            else:
                print("\n⚠️ Analysis needs revision before proceeding")
                return result.content

        except Exception as e:
            print(f"\n❌ Error in analysis process: {e}")
            return f"Error executing agent: {str(e)}"

    def _format_technical_analysis(self, content: str) -> str:
        """Format technical analysis as markdown"""
        sections = [
            "# Technical Requirements Analysis\n",
            "## Overview\n",
            "## Components\n",
            "## Technical Specifications\n",
            "## Implementation Details\n"
        ]
        
        formatted = sections[0]
        
        # Extract and format each section
        if "OVERVIEW:" in content:
            overview = content.split("OVERVIEW:")[1].split("COMPONENTS:")[0].strip()
            formatted += f"{sections[1]}{overview}\n\n"
            
        if "COMPONENTS:" in content:
            components = content.split("COMPONENTS:")[1].split("TECHNICAL SPECIFICATIONS:")[0].strip()
            formatted += f"{sections[2]}{components}\n\n"
            
        if "TECHNICAL SPECIFICATIONS:" in content:
            specs = content.split("TECHNICAL SPECIFICATIONS:")[1].split("IMPLEMENTATION DETAILS:")[0].strip()
            formatted += f"{sections[3]}{specs}\n\n"
            
        if "IMPLEMENTATION DETAILS:" in content:
            impl = content.split("IMPLEMENTATION DETAILS:")[1].strip()
            formatted += f"{sections[4]}{impl}\n"
            
        return formatted

