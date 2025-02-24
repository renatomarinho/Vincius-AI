import os
import yaml
import time
import google.generativeai as genai
from typing import Dict, Any, Optional
from pathlib import Path
from .config_manager import ConfigManager

class BrainModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrainModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.max_retries = 3
        self.retry_delay = 1
        self.model = None
        self.config_manager = ConfigManager()

        print("🔄 Initializing Google Generative AI...")
        genai.configure(api_key=self.config_manager.api_key)
        
        self._initialize_model(self.default_model_config)
        print(f"✅ Model initialized with {self.default_sleep}s default sleep time")

    @property
    def default_sleep(self) -> int:
        return self.config_manager.get('MODEL_SLEEP_TIME', {}).get('default', 10)

    @property
    def default_model_config(self) -> Dict:
        return self.config_manager.get('MODEL_CONFIG')

    @property
    def min_sleep(self) -> int:
        """Get minimum sleep time"""
        return self.config_manager.get('MODEL_SLEEP_TIME', {}).get('min', 5)

    @property
    def max_sleep(self) -> int:
        """Get maximum sleep time"""
        return self.config_manager.get('MODEL_SLEEP_TIME', {}).get('max', 30)

    @property
    def operation_sleeps(self) -> Dict:
        """Get operation-specific sleep times"""
        return self.config_manager.get('MODEL_SLEEP_TIME', {}).get('operations', {})

    def get_sleep_time(self, operation: str = None) -> int:
        """Get sleep time for specific operation or default"""
        if operation and operation in self.operation_sleeps:
            sleep_time = self.operation_sleeps[operation]
        else:
            sleep_time = self.default_sleep
            
        # Ensure sleep time is within bounds
        return max(min(sleep_time, self.max_sleep), self.min_sleep)

    def generate(self, prompt: str, model_config: Dict[str, Any]) -> Optional[str]:
        """Generate content with improved retry mechanism and rate limiting handling"""
        # Only update model if configuration changes, don't reconfigure API
        current_model = getattr(self.model, 'model_name', None)
        if model_config.get('model') != current_model:
            print(f"Switching model from {current_model} to {model_config.get('model')}")
            self._initialize_model(model_config)
        
        base_wait_time = 10  # Start with 10 seconds
        for attempt in range(self.max_retries):
            try:
                print(f"\n🤖 Generating content (attempt {attempt + 1}/{self.max_retries})...")
                
                # Exponential backoff wait time
                if attempt > 0:
                    wait_time = base_wait_time * (2 ** (attempt - 1))  # Exponential backoff
                    print(f"⏳ Waiting {wait_time} seconds before retry (rate limit backoff)...")
                    time.sleep(wait_time)

                # Generate response
                response = self.model.generate_content(prompt)
                
                # Validate response
                if not response or not hasattr(response, 'text'):
                    raise ValueError("Invalid response format from model")
                
                text = response.text
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("Empty or invalid response text")
                
                print("✅ Content generated successfully")
                return text

            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Generation attempt {attempt + 1} failed: {error_str}")
                
                # Handle specific error types
                if "429" in error_str or "quota" in error_str.lower():
                    print("📢 Rate limit or quota exceeded. Using longer backoff...")
                    base_wait_time *= 2  # Double the base wait time for rate limits
                
                if attempt == self.max_retries - 1:
                    print("\n❌ All generation attempts failed")
                    if "429" in error_str or "quota" in error_str.lower():
                        print("💡 Suggestion: Wait a few minutes before trying again or check your API quota")
                    return None

        return None

    def _initialize_model(self, config: Dict[str, Any]) -> None:
        """Initialize the model with configuration"""
        try:
            # Extract model name from config
            model_name = config.pop('model', 'gemini-pro')
            
            # Get generation config without model name
            generation_config = {
                "temperature": config.get('temperature'),
                "top_p": config.get('top_p'),
                "top_k": config.get('top_k'),
                "max_output_tokens": config.get('max_tokens')
            }
            
            # Remove None values
            generation_config = {k: v for k, v in generation_config.items() if v is not None}
            
            safety_settings = self.config_manager.get('SAFETY_SETTINGS')
            
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            print(f"✅ Model {model_name} initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing model: {e}")
            raise
