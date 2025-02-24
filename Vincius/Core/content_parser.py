import re
from typing import List, Dict, Any

class ContentParser:
    @staticmethod
    def parse_files_section(content: str) -> List[Dict[str, Any]]:
        """Parse content into file information dictionaries"""
        print("\n🔍 DEBUG: Content Parser Start")
        print("=" * 50)
        
        if not content:
            print("⚠️ DEBUG: Empty content received")
            return []

        print(f"📝 DEBUG: Raw content preview (first 500 chars):")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        files_info = []
        
        # Look for file markers
        file_pattern = r"FILE:\s*([^\n]+)\nType:\s*([^\n]+)\nDescription:\s*([^\n]+)\nContent:\n(.*?)(?=FILE:|$)"
        matches = list(re.finditer(file_pattern, content, re.DOTALL))
        
        print(f"🔍 DEBUG: Found {len(matches)} file pattern matches")
        
        for match in matches:
            path = match.group(1).strip()
            file_type = match.group(2).strip()
            description = match.group(3).strip()
            content = match.group(4).strip()
            
            print("\n📄 DEBUG: File Section Found:")
            print(f"- Path: {path}")
            print(f"- Type: {file_type}")
            print(f"- Description: {description}")
            print(f"- Content length: {len(content)}")
            print(f"- Content preview: {content[:100]}...")
            
            files_info.append({
                "path": path,
                "type": file_type,
                "description": description,
                "content": content
            })

        # If no structured format found, try alternative
        if not files_info:
            print("\n🔄 DEBUG: Trying alternative format")
            # Try markdown style
            alt_pattern = r"```(\w+)\n(.*?)```"
            alt_matches = list(re.finditer(alt_pattern, content, re.DOTALL))
            print(f"🔍 DEBUG: Found {len(alt_matches)} markdown-style matches")
            
            for match in alt_matches:
                file_type = match.group(1)
                content = match.group(2).strip()
                
                path = "docs/technical_requirements.md" if "technical" in content.lower() else f"docs/output.{file_type}"
                
                print("\n📄 DEBUG: Alternative Format Found:")
                print(f"- Path: {path}")
                print(f"- Type: {file_type}")
                print(f"- Content length: {len(content)}")
                print(f"- Content preview: {content[:100]}...")
                
                files_info.append({
                    "path": path,
                    "type": file_type,
                    "description": "Generated content",
                    "content": content
                })

        print("\n✅ DEBUG: Content Parser Result:")
        print(f"Total files to create: {len(files_info)}")
        for info in files_info:
            print(f"- {info['path']} ({len(info['content'])} chars)")
        
        print("=" * 50)
        return files_info
