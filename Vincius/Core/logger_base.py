import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import hashlib
from Vincius.Core.config_manager import ConfigManager  # Add this import

class LoggerBase:
    VALID_AGENTS = {
        "Developer": "development_logs",
        "Analyst": "analysis_logs",
        "Reviewer": "review_logs",
        "Tester": "testing_logs",
        "Deployer": "deployment_logs"
    }

    def __init__(self, base_path: Path, agent_type: str):
        """Initialize logger with specific agent type"""
        if agent_type not in self.VALID_AGENTS:
            raise ValueError(f"Invalid agent type. Must be one of: {', '.join(self.VALID_AGENTS.keys())}")
            
        self.agent_type = agent_type
        config = ConfigManager()
        logs_dir = config.base_path / config.get('PATHS.logs_dir', 'Logs')  # Use config for logs directory
        
        self.log_dir = logs_dir / agent_type
        self.log_file = self.log_dir / f"{self.VALID_AGENTS[agent_type]}.json"
        self._initialize_log_directory()
        print(f"📝 {agent_type} logs will be saved to: {self.log_file}")

    def _initialize_log_directory(self):
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            if not self.log_file.exists():
                self._write_log_file([])
                print(f"✅ Initialized new log file at: {self.log_file}")
        except Exception as e:
            print(f"❌ Error initializing log directory: {e}")
            raise

    def _read_log_file(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.log_file.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_log_file(self, logs: List[Dict[str, Any]]):
        self.log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

    def _get_file_version(self, file_path: str, content: str) -> int:
        """Get the next version number for a file"""
        logs = self._read_log_file()
        versions = [log.get('version', 1) for log in logs 
                   if log['file_path'] == file_path]
        return max(versions, default=0) + 1

    def _calculate_hash(self, content: str) -> str:
        """Calculate hash of file content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def log_file_creation(self, file_path: Path, description: str = "", 
                         is_modification: bool = False, content: str = ""):
        """Log a file creation or modification event with version control"""
        logs = self._read_log_file()
        file_path_str = str(file_path)
        
        # Get file content if not provided
        if not content and file_path.exists():
            content = file_path.read_text(encoding='utf-8')

        # Calculate content hash
        content_hash = self._calculate_hash(content) if content else ""
        
        # Check if this exact content was already logged
        for log in logs:
            if (log['file_path'] == file_path_str and 
                log.get('content_hash') == content_hash):
                print(f"⚠️ Skipping log: identical content already exists")
                return

        # Get next version number
        version = self._get_file_version(file_path_str, content)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path_str,
            "operation": "modification" if is_modification else "creation",
            "description": description,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "version": version,
            "content_hash": content_hash
        }
        
        logs.append(log_entry)
        self._write_log_file(logs)
        print(f"📝 Logged {log_entry['operation']} of {file_path_str} (v{version})")

    def get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get version history of a specific file"""
        logs = self._read_log_file()
        history = [log for log in logs if log["file_path"] == file_path]
        return sorted(history, key=lambda x: x.get('version', 1))
