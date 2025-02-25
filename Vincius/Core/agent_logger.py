from pathlib import Path
from typing import Dict, Any, List, Optional
import os
from Vincius.Core.logger_base import LoggerBase

class AgentLogger(LoggerBase):
    """Universal logger for all agent types"""
    
    def __init__(self, base_path: Path, agent_type: str, agent_uuid: str = None, agent: Any = None):
        # Try to get the UUID from the agent object if provided
        if agent and hasattr(agent, 'uuid'):
            agent_uuid = agent.uuid
        # Fall back to environment variable if still not set
        elif agent_uuid is None:
            agent_uuid = os.environ.get('CURRENT_AGENT_UUID', 'unknown')
            
        super().__init__(base_path, agent_type, agent_uuid)
        print(f"📝 Logger initialized for agent {agent_type} with UUID: {agent_uuid[:8] if agent_uuid else 'unknown'}")
        
    def log_file_creation(self, file_path: Path, description: str = "", 
                         is_modification: bool = False, content: str = ""):
        """Log a file creation or modification event"""
        super().log_file_creation(
            file_path=file_path,
            description=description,
            is_modification=is_modification,
            content=content
        )

    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recently created/modified files"""
        logs = self._read_log_file()
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
    def get_files_by_agent(self, agent_uuid: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files created/modified by specific agent instance"""
        logs = self._read_log_file()
        
        # If no UUID provided, use the current agent's UUID
        if agent_uuid is None:
            agent_uuid = self.agent_uuid
            
        return [log for log in logs if log.get("agent_uuid") == agent_uuid]
        
    def get_current_agent_files(self) -> List[Dict[str, Any]]:
        """Get files created/modified by the current agent instance"""
        return self.get_files_by_agent(self.agent_uuid)
