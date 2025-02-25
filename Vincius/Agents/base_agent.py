from typing import Dict, Any, Optional, List, Callable
import yaml
import time
import os
import uuid  # Add UUID import
from abc import ABC
from Vincius.Core.config_manager import ConfigManager

class BaseAgent(ABC):
    """Base class for all agents with retry functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize base agent with configuration"""
        self.config = config
        self.max_retries = 3
        self.retry_delay = 10  # seconds
        self.name = None  # Add name property
        self.uuid = str(uuid.uuid4())  # Generate unique identifier
        
        # Initialize base directory from config
        config_manager = ConfigManager()
        base_dir_key = config.get('base_dir_key', '').lower()
        self.base_dir = config_manager.get_base_path(base_dir_key)
        
        # Clear previous agent type before setting new one
        if 'CURRENT_AGENT_TYPE' in os.environ:
            del os.environ['CURRENT_AGENT_TYPE']
            
        # Set current agent type
        os.environ['CURRENT_AGENT_TYPE'] = self.__class__.__name__.replace('Agent', '')
        os.environ['CURRENT_AGENT_UUID'] = self.uuid  # Store UUID in environment
        print(f"🔄 Switched to agent: {os.environ['CURRENT_AGENT_TYPE']} (ID: {self.uuid[:8]})")
        
        # Moved from individual agent classes to make it consistent
        agent_type = self.name or self.__class__.__name__.replace('Agent', '')
        print(f"🔧 Initialized {agent_type} agent with UUID: {self.uuid[:8]} in {self.base_dir}")

    def __del__(self):
        """Cleanup when agent is destroyed"""
        if 'CURRENT_AGENT_TYPE' in os.environ:
            del os.environ['CURRENT_AGENT_TYPE']
        if 'CURRENT_AGENT_UUID' in os.environ:
            del os.environ['CURRENT_AGENT_UUID']
        print(f"🧹 Cleaned up agent environment")

    @property
    def agent_type(self) -> str:
        """Get the current agent type"""
        return self.name or self.__class__.__name__.replace('Agent', '')
        
    @property
    def agent_id(self) -> str:
        """Get the agent's unique identifier"""
        return self.uuid

    def _retry_on_failure(self, prompt: str, brain: Any, error_msg: str = "") -> Optional[str]:
        """Retry functionality for model requests with better error handling"""
        current_try = 0
        last_error = None

        while current_try < self.max_retries:
            try:
                result = brain.generate(prompt, self.config)
                
                # Check for empty or invalid response
                if not result or not isinstance(result, str) or len(result.strip()) == 0:
                    raise ValueError("Empty or invalid response from model")

                return result

            except Exception as e:
                current_try += 1
                last_error = e
                print(f"\n⚠️ Attempt {current_try} failed: {e}")
                print(f"Error details: {error_msg}" if error_msg else "")
                
                if current_try < self.max_retries:
                    wait_time = self.retry_delay * current_try
                    print(f"\n🔄 Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    print(f"🔄 Retrying... (Attempt {current_try + 1}/{self.max_retries})")
                else:
                    print("\n❌ Max retries reached. Operation failed.")

        return None

    def _validate_yaml(self, content: str) -> Optional[Dict]:
        """Validate YAML content with retry"""
        if not content or "files:" not in content:
            return None

        try:
            yaml_content = content[content.find("files:"):]
            return yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"⚠️ Invalid YAML structure: {e}")
            return None

    def execute(self, input_data: Any = None) -> Any:
        raise NotImplementedError("Agents must implement execute method")
