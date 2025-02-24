from typing import Dict, Any, Optional, List, Callable
import yaml
import time

class BaseAgent:
    """Base class for all agents with retry functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_retries = 3
        self.retry_delay = 10  # seconds

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
