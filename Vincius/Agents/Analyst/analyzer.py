from typing import Dict, Any, NamedTuple
from pathlib import Path
import json
from Vincius.Agents.Analyst.prompts import AnalystPrompts

class AnalysisResult(NamedTuple):
    content: str
    structured_content: Dict[str, Any]

class RequirementsAnalyzer:
    def analyze_requirements(self, requirements: str, brain: Any, config: Dict) -> AnalysisResult:
        """Analyze requirements and generate technical analysis"""
        try:
            prompt = AnalystPrompts.requirements_analysis(requirements, config.get('prompt', ''))
            result = brain.generate(prompt, config)
            
            # Parse structured content
            structured_content = self._extract_sections(result)
            if not structured_content:
                print("⚠️ No valid analysis structure found")
                print("\nRaw response:")
                print(result[:500] + "..." if len(result) > 500 else result)
                return AnalysisResult(result, {})
                
            print("✅ Analysis generated successfully")
            return AnalysisResult(result, structured_content)
            
        except Exception as e:
            print(f"❌ Error analyzing requirements: {e}")
            return AnalysisResult("Error in analysis", {})

    def _extract_sections(self, text: str) -> Dict[str, Any]:
        """Extract structured content from the analysis text"""
        try:
            sections = {
                'overview': '',
                'components': [],
                'technical_specifications': {},
                'implementation_details': []
            }
            
            current_section = None
            current_content = []
            
            for line in text.splitlines():
                clean_line = line.strip()
                if not clean_line:
                    continue

                # Detect section headers
                lower_line = clean_line.lower()
                if 'overview:' in lower_line:
                    current_section = 'overview'
                    current_content = []
                elif 'components:' in lower_line:
                    current_section = 'components'
                    current_content = []
                elif 'technical specifications:' in lower_line:
                    current_section = 'technical_specifications'
                    current_content = []
                elif 'implementation details:' in lower_line:
                    current_section = 'implementation_details'
                    current_content = []
                elif current_section:
                    current_content.append(clean_line)
                    
                    # Process completed section
                    if len(current_content) > 0 and (
                        'overview' in lower_line or 
                        'components' in lower_line or 
                        'technical' in lower_line or 
                        'implementation' in lower_line
                    ):
                        sections[current_section] = self._process_section(
                            current_section, 
                            current_content
                        )
                        current_content = []

            # Process last section
            if current_section and current_content:
                sections[current_section] = self._process_section(
                    current_section, 
                    current_content
                )

            return sections

        except Exception as e:
            print(f"❌ Error extracting sections: {e}")
            return {}

    def _process_section(self, section: str, content: list[str]) -> Any:
        """Process content based on section type"""
        if not content:
            return "" if section == 'overview' else []
            
        if section == 'overview':
            return '\n'.join(content)
            
        if section == 'components':
            components = []
            current_component = {}
            for line in content:
                if line.startswith('- Name:'):
                    if current_component:
                        components.append(current_component)
                    current_component = {'name': line[7:].strip()}
                elif line.startswith('  Description:'):
                    current_component['description'] = line[14:].strip()
            if current_component:
                components.append(current_component)
            return components
            
        if section == 'technical_specifications':
            specs = {}
            current_key = None
            current_items = []
            for line in content:
                if line.startswith('- '):
                    if current_key and current_items:
                        specs[current_key] = current_items
                        current_items = []
                    current_key = line[2:].lower()
                elif current_key:
                    current_items.append(line.strip())
            if current_key and current_items:
                specs[current_key] = current_items
            return specs
            
        return content
