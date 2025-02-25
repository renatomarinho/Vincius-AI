from Vincius.Core.logger_base import LoggerBase
from pathlib import Path
from typing import Dict, Any, List

class AnalystLogger(LoggerBase):
    def __init__(self, base_path: Path):
        super().__init__(base_path, "Analyst")

    def get_documentation_history(self) -> List[Dict[str, Any]]:
        """Get history of documentation files"""
        logs = self._read_log_file()
        return [log for log in logs if 'Docs' in log["file_path"]]

    def get_recent_analysis(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recent analysis files"""
        logs = self._read_log_file()
        doc_logs = [log for log in logs if 'Docs' in log["file_path"]]
        return sorted(doc_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
