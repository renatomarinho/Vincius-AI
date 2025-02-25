import re
from typing import List, Dict, Any, Optional
import commonmark

class ContentParser:
    def __init__(self):
        self.parser = commonmark.Parser()
        self.renderer = commonmark.HtmlRenderer()

    @staticmethod
    def clean_code_block(content: str) -> str:
        """Clean content from markdown code blocks and extra formatting"""
        # Remove markdown code blocks (triple backticks)
        content = re.sub(r'^```[a-zA-Z]*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```$', '', content, flags=re.MULTILINE)
        
        # Replace "CONTENT_START"/"CONTENT_END" markers (alternative format)
        content = re.sub(r'CONTENT_START\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\nCONTENT_END', '', content, flags=re.MULTILINE)
        
        return content.strip()

    @classmethod
    def parse_files_section(cls, content: str) -> List[Dict[str, Any]]:
        """Parse file sections from content string"""
        if not content:
            print("⚠️ Empty content provided to parser")
            return []
            
        # First try standard parsing approach
        files = cls._try_standard_parsing(content)
        if files:
            return files
            
        # Try direct file header detection
        files = cls._try_direct_file_header_parsing(content)
        if files:
            return files
            
        # Last resort: markdown blocks and other patterns
        files = cls._try_fallback_parsing(content)
        if files:
            return files
            
        print("⚠️ No file sections found in the content")
        print(f"Content preview:\n{content[:200]}...")
        return []
    
    @classmethod
    def _try_standard_parsing(cls, content: str) -> List[Dict[str, Any]]:
        """Try standard pattern parsing first"""
        files = []
        
        # Look for FILE: pattern
        pattern = r'FILE:\s*(.*?)[\n\r]+.*?Content:[\n\r]+(.*?)(?=FILE:|$)'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            filepath = match.group(1).strip()
            file_content = match.group(2).strip()
            
            # Extract description if present
            desc_match = re.search(r'Description:\s*(.*?)[\n\r]+', 
                                  content[match.start():match.end()], 
                                  re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ""
            
            files.append({
                "path": filepath,
                "content": file_content,
                "description": description,
                "modifications": False
            })
        
        if files:
            print(f"✅ Found {len(files)} file sections using standard pattern")
            
        return files
    
    @classmethod
    def _try_direct_file_header_parsing(cls, content: str) -> List[Dict[str, Any]]:
        """Try to parse by looking for file headers directly"""
        files = []
        
        # Split by "FILE:" but keep the delimiter
        parts = re.split(r'(FILE:[\s]*[^\n]+)', content, flags=re.IGNORECASE)
        
        # Skip the first part if it doesn't contain a FILE: header
        if not parts[0].strip().upper().startswith('FILE:'):
            parts = parts[1:]
            
        # Process pairs of header + content
        for i in range(0, len(parts), 2):
            if i + 1 >= len(parts):
                break
                
            header = parts[i].strip()
            body = parts[i + 1].strip()
            
            # Extract filepath from header
            filepath = header.replace('FILE:', '', 1).strip()
            
            # Look for description in body
            desc_match = re.search(r'Description:[\s]*([^\n]+)', body, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract content - everything after Content: or the whole body if not found
            content_match = re.search(r'Content:[\s]*\n(.*)', body, re.DOTALL | re.IGNORECASE)
            file_content = content_match.group(1).strip() if content_match else body
            
            files.append({
                "path": filepath,
                "content": file_content,
                "description": description,
                "modifications": False
            })
        
        if files:
            print(f"✅ Found {len(files)} file sections using direct header parsing")
            
        return files
    
    @classmethod
    def _try_fallback_parsing(cls, content: str) -> List[Dict[str, Any]]:
        """Try fallback parsing methods"""
        # Combine markdown blocks and filepath patterns
        files = cls._extract_from_markdown_blocks(content)
        if not files:
            files = cls._extract_filepath_and_content(content)
            
        if files:
            print(f"✅ Found {len(files)} file sections using fallback parsing")
            
        return files

    @staticmethod
    def _extract_file_sections(content: str) -> List[str]:
        """Extract file sections from content"""
        if not content:
            return []
            
        # Look for FILE: pattern
        pattern = r'(?:FILE|file|Path):\s*([^\n]+)(?:\s*.*?\s*.*?)(?:(?:Content:|CONTENT_START)\s*(.*?)(?:CONTENT_END|\n\s*FILE:|$))'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            return []
            
        file_sections = []
        last_end = 0
        
        for match in re.finditer(pattern, content, re.DOTALL):
            section = content[match.start():match.end()]
            file_sections.append(section)
            last_end = match.end()
            
        # If there's only one section and it doesn't end properly, include the rest
        if len(file_sections) == 1 and last_end < len(content):
            file_sections[0] += content[last_end:]
            
        return file_sections

    @staticmethod
    def _parse_file_section(section: str) -> Optional[Dict[str, Any]]:
        """Parse a file section into a file info dictionary"""
        # Extract file path
        path_match = re.search(r'(?:FILE|file|Path):\s*([^\n]+)', section, re.IGNORECASE)
        if not path_match:
            return None
        file_path = path_match.group(1).strip()
        
        # Extract description if present
        desc_match = re.search(r'Description:\s*([^\n]+)', section, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Handle both Content: and CONTENT_START formats
        if "CONTENT_START" in section:
            content_match = re.search(r'CONTENT_START\s*(.*?)(?:CONTENT_END|$)', section, re.DOTALL)
        else:
            content_match = re.search(r'Content:\s*(.*?)$', section, re.DOTALL)
        
        if not content_match:
            # Try a more lenient approach - extract everything after the header lines
            header_end = path_match.end()
            if desc_match:
                header_end = max(header_end, desc_match.end())
            
            content = section[header_end:].strip()
        else:
            content = content_match.group(1).strip()
        
        # Check for modifications flag
        is_modification = bool(re.search(r'modifications:\s*true', section, re.IGNORECASE))
        
        return {
            "path": file_path,
            "description": description,
            "content": content,
            "modifications": is_modification
        }

    @classmethod
    def _extract_from_markdown_blocks(cls, content: str) -> List[Dict[str, Any]]:
        """Extract files from markdown code blocks"""
        files = []
        
        # Look for markdown blocks with filepath comments
        pattern = r'```[a-zA-Z]*\n(?:\/\/|#)\s*filepath:\s*([^\n]+)\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            filepath = match.group(1).strip()
            file_content = match.group(2).strip()
            
            files.append({
                "path": filepath,
                "content": file_content,
                "description": f"File extracted from markdown block",
                "modifications": False
            })
            
        return files

    @classmethod
    def _extract_filepath_and_content(cls, content: str) -> List[Dict[str, Any]]:
        """Last resort extraction - look for filepath indicators and subsequent content"""
        files = []
        
        # Try to find filepath patterns followed by content
        patterns = [
            r'(?:filepath|path|file):\s*([^\n]+)\s*\n\s*```[a-zA-Z]*\n(.*?)```',
            r'Create file (?:at|in) `([^`]+)`[^`]*```[a-zA-Z]*\n(.*?)```',
            r'([a-zA-Z0-9_\-\/\.]+\.[a-zA-Z0-9]+)\s*\n\s*```[a-zA-Z]*\n(.*?)```'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                filepath = match.group(1).strip()
                file_content = match.group(2).strip()
                
                files.append({
                    "path": filepath,
                    "content": file_content,
                    "description": "File extracted using fallback pattern",
                    "modifications": False
                })
        
        return files
