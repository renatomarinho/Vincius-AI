import re
from typing import List, Dict, Any
import commonmark

class ContentParser:
    def __init__(self):
        self.parser = commonmark.Parser()
        self.renderer = commonmark.HtmlRenderer()

    @staticmethod
    def parse_files_section(content: str) -> List[Dict[str, Any]]:
        """Parse content into file information dictionaries"""
        print("\n🔍 DEBUG: Content Parser Start")
        
        if not content:
            print("⚠️ DEBUG: Empty content received")
            return []

        files_info = []
        
        # Try each pattern in order of preference
        patterns = [
            # Pattern 1: Full format with CONTENT_START/END
            r"FILE:\s*([^\n]+)\nType:\s*([^\n]+)\nDescription:\s*([^\n]+)\nCONTENT_START\n(.*?)\nCONTENT_END",
            
            # Pattern 2: Simple format with Content: marker
            r"FILE:\s*([^\n]+)\nType:\s*([^\n]+)\nDescription:\s*([^\n]+)\nContent:\n(.*?)(?=(?:FILE:|$))",
            
            # Pattern 3: Markdown style with filepath comment
            r"```(\w+)\n(?:#|//)\s*filepath:\s*(.+?)\n(.*?)```"
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, content, re.DOTALL))
            if matches:
                print(f"🔍 DEBUG: Found matches using pattern: {pattern[:30]}...")
                
                for match in matches:
                    if len(match.groups()) == 4:  # Patterns 1 and 2
                        path = match.group(1).strip()
                        file_type = match.group(2).strip()
                        description = match.group(3).strip()
                        content = match.group(4).strip()
                    else:  # Pattern 3
                        file_type = match.group(1)
                        path = match.group(2).strip()
                        content = match.group(3).strip()
                        description = "Generated content"
                    
                    print(f"\n📄 DEBUG: Found file section:")
                    print(f"Path: {path}")
                    print(f"Type: {file_type}")
                    print(f"Content length: {len(content)}")
                    
                    files_info.append({
                        "path": path,
                        "type": file_type,
                        "description": description,
                        "content": content
                    })
                
                break  # Use first pattern that finds matches
        
        print(f"\n✅ DEBUG: Found {len(files_info)} files")
        for info in files_info:
            print(f"- {info['path']} ({len(info['content'])} chars)")
        
        return files_info

    @staticmethod
    def clean_code_block(content: str) -> str:
        """Remove any code block markers from content using commonmark"""
        if not content:
            return ""
        
        parser = commonmark.Parser()
        ast = parser.parse(content)
        
        # Walk AST to find code blocks
        for node in ast.walker():
            if node[0].t == 'code_block':
                return node[0].literal.strip()
        
        # If no code block found, return cleaned content
        content = re.sub(r'^```\w*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'```\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'^(?:#|//)\s*filepath:.*\n?', '', content, flags=re.MULTILINE)
        
        return content.strip()
