import os
from pathlib import Path
import yaml
from typing import Any, Dict, Optional

class ConfigManager:
    _instance = None
    _config = None
    _base_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_config()

    @classmethod
    def _get_project_root(cls) -> Path:
        """Get project root directory"""
        if not cls._base_path:
            current_file = Path(__file__).resolve()
            
            # First try: Look for main.py
            current_dir = current_file 
            while current_dir.parent != current_dir:
                if (current_dir.parent / "main.py").exists():
                    cls._base_path = current_dir.parent
                    break
                current_dir = current_dir.parent

            # Second try: Use main module path
            if not cls._base_path:
                import sys
                if hasattr(sys.modules['__main__'], '__file__'):
                    cls._base_path = Path(sys.modules['__main__'].__file__).parent.resolve()
            
            # Last resort: use current working directory
            if not cls._base_path:
                cls._base_path = Path.cwd()
            
            print(f"📂 Project root identified as: {cls._base_path}")
            print(f"📂 Main.py location: {(cls._base_path / 'main.py').absolute()}")
            
        return cls._base_path.resolve()

    @property
    def base_path(self) -> Path:
        """Get base path for the project"""
        return self._get_project_root()

    def _create_default_config(self, config_path: Path) -> None:
        """Create default config.yaml file"""
        default_config = {
            'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', ''),
            'PATHS': {
                'codebase_dir': 'Codebase'  # Relative to project root, not package
            },
            'MODEL_CONFIG': {
                'model': 'gemini-pro',
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_tokens': 2048
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(default_config, f)
        print(f"✅ Created default config at: {config_path}")
        return default_config

    def _create_default_workflow(self, workflow_path: Path) -> None:
        """Create default workflow.yaml file"""
        workflow_config = {
            'workflow': {
                'Analysis': {
                    'description': 'Analyze and document the requirements.',
                    'responsible_department': 'ANALYSIS',
                    'action': {
                        'type': 'class_execution',
                        'class': 'AnalystAgent',
                        'module': 'Vincius.Agents.Analyst.agent'
                    },
                    'next_steps': {
                        'success_step': 'TaskManager'
                    }
                }
            }
        }
        
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        with open(workflow_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(workflow_config, f)
        print(f"✅ Created default workflow at: {workflow_path}")

    def _load_config(self) -> None:
        """Load configuration from multiple sources with priority"""
        self._config = {}
        
        config_path = self.base_path / "Vincius/Config" / "config.yaml"
        workflow_path = self.base_path / "Vincius/Config" / "Workflows" / "workflow.yaml"
        
        print(f"Looking for config at: {config_path}")
        print(f"Looking for workflow at: {workflow_path}")
        
        try:
            # Load or create main config
            if not config_path.exists():
                self._config = self._create_default_config(config_path)
            else:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                    print(f"✅ Loaded config from: {config_path.absolute()}")
            
            # Load or create workflow config
            if not workflow_path.exists():
                self._create_default_workflow(workflow_path)
            
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_config = yaml.safe_load(f) or {}
                self._config['workflow'] = workflow_config.get('workflow', {})
                print(f"✅ Loaded workflow from: {workflow_path.absolute()}")
                print(f"Found {len(self._config['workflow'])} workflow steps")
            
        except Exception as e:
            print(f"⚠️ Failed to load config: {e}")
            print(f"Current working directory: {Path.cwd()}")
            print(f"Config manager file location: {Path(__file__).resolve()}")
            self._config = {}
        
        # Set defaults if needed
        self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default configurations if not present"""
        defaults = {
            'MODEL_SLEEP_TIME': {
                'default': 10,
                'min': 5,
                'max': 30,
                'operations': {}
            },
            'MODEL_CONFIG': {
                'model': 'gemini-pro',
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_tokens': 2048
            },
            'SAFETY_SETTINGS': [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ],
            'MODEL_GENERATION_CONFIG': {
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048
            }
        }
        
        for key, value in defaults.items():
            if key not in self._config:
                self._config[key] = value

    def get_generation_config(self, custom_config: Dict = None) -> Dict:
        """Get model generation configuration, optionally merged with custom config"""
        base_config = self.get('MODEL_GENERATION_CONFIG', {})
        if custom_config:
            return {**base_config, **custom_config}
        return base_config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)

    def get_all(self) -> Dict:
        """Get all configuration values"""
        return self._config.copy()

    @property
    def api_key(self) -> Optional[str]:
        """Get API key with priority from env var"""
        return os.environ.get('GOOGLE_API_KEY', self._config.get('GOOGLE_API_KEY'))

    @property
    def workflow(self) -> Dict:
        """Get workflow configuration"""
        return self.get('workflow', {})

    @property
    def codebase_path(self) -> Path:
        """Get codebase directory path relative to project root"""
        # Always use base_path (project root) for codebase
        codebase = self.base_path / self.get('PATHS', {}).get('codebase_dir', 'Codebase')
        codebase.mkdir(parents=True, exist_ok=True)
        print(f"📂 Using codebase directory: {codebase.absolute()}")
        return codebase
