import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from Vincius.Core.logger_base import LoggerBase

class DeveloperLogger(LoggerBase):
    def __init__(self, base_path: Path):
        super().__init__(base_path, "Developer")

    def _initialize_log_directory(self):
        """Create log directory and file if they don't exist"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)  # Added parents=True for nested creation
            if not self.log_file.exists():
                self._write_log_file([])
                print(f"✅ Initialized new log file at: {self.log_file}")
        except Exception as e:
            print(f"❌ Error initializing log directory: {e}")
            raise

    def _read_log_file(self) -> List[Dict[str, Any]]:
        """Read the current log file"""
        try:
            return json.loads(self.log_file.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_log_file(self, logs: List[Dict[str, Any]]):
        """Write logs to the log file"""
        self.log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

    def log_file_creation(self, file_path: Path, description: str = "", 
                         is_modification: bool = False, content: str = ""):
        """Log a file creation or modification event"""
        super().log_file_creation(
            file_path=file_path,
            description=description,
            is_modification=is_modification,
            content=content
        )

    def get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get history of operations for a specific file"""
        logs = self._read_log_file()
        return [log for log in logs if log["file_path"] == file_path]

    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently created/modified files"""
        logs = self._read_log_file()
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
