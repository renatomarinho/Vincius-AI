from typing import Dict, Any, List
from Vincius.Agents.Analyst.prompts import AnalystPrompts

class AnalysisReviewer:
    def __init__(self):
        self.prompts = AnalystPrompts()

    def review_analysis(self, analysis: str, brain: Any, config: Dict) -> bool:
        """Review the generated analysis"""
        try:
            print("\n🔍 Reviewing analysis...")
            
            # Generate review using prompt
            review_prompt = self.prompts.review_analysis(analysis)
            review_result = brain.generate(review_prompt, config)
            
            if "VALIDATION_PASSED" in review_result:
                print("✅ Analysis validation passed - All requirements met")
                return True
            
            # If improvements needed, display them
            if "IMPROVEMENTS NEEDED" in review_result:
                self._display_improvements(review_result)
                
                # Get missing sections
                missing_sections = self._get_missing_sections(analysis)
                if missing_sections:
                    improvement_prompt = self.prompts.request_improvements(missing_sections)
                    print("\n📝 Requested improvements:")
                    print(improvement_prompt)
                
            return False
            
        except Exception as e:
            print(f"❌ Error reviewing analysis: {e}")
            return False

    def _get_missing_sections(self, analysis: str) -> List[str]:
        """Identify missing sections in the analysis"""
        required_sections = ["OVERVIEW:", "COMPONENTS:", "TECHNICAL SPECIFICATIONS:"]
        return [section for section in required_sections if section not in analysis]

    def _display_improvements(self, review_result: str) -> None:
        """Display improvement suggestions"""
        improvements = review_result.split("IMPROVEMENTS NEEDED:")[1].strip()
        print("\n⚠️ Required Improvements:")
        for line in improvements.splitlines():
            if line.strip():
                print(f"  • {line.strip()}")
