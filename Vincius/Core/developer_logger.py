import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class DeveloperLogger:
    def __init__(self, base_path: Path):
        self.log_dir = base_path / "Log" / "Developer"  # Changed to use Log/Developer directory
        self.log_file = self.log_dir / "file_creation_log.json"
        self._initialize_log_directory()
        print(f"📝 Developer logs will be saved to: {self.log_dir}")

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

    def log_file_creation(self, file_path: Path, description: str = "", is_modification: bool = False):
        """Log a file creation or modification event"""
        logs = self._read_log_file()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": str(file_path),
            "operation": "modification" if is_modification else "creation",
            "description": description,
            "file_size": file_path.stat().st_size if file_path.exists() else 0
        }
        
        logs.append(log_entry)
        self._write_log_file(logs)

    def get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get history of operations for a specific file"""
        logs = self._read_log_file()
        return [log for log in logs if log["file_path"] == file_path]

    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently created/modified files"""
        logs = self._read_log_file()
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
