"""
Configuration management for the multi-agent system
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the application"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # OpenRouter Configuration
        self.use_openrouter = os.getenv('USE_OPENROUTER', 'false').lower() == 'true'
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.openrouter_base_url = 'https://openrouter.ai/api/v1'
        
        # Model Configuration
        # Model Configuration
        self.model_name = os.getenv('MODEL_NAME', 'google/gemini-2.0-flash-exp:free')
        
        # Force switch if using known problematic models
        if 'stepfun' in self.model_name or 'phi-3' in self.model_name:
            print(f"[Config] Detected problematic model '{self.model_name}'. Auto-switching to Gemini 2.0 Flash.")
            self.model_name = 'google/gemini-2.0-flash-exp:free'
            
        self.max_tokens = int(os.getenv('MAX_TOKENS', '4096'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        
        # Azure OpenAI (optional)
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', '')
        
        # Local model (optional)
        self.use_local_model = os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true'
        self.local_model_base_url = os.getenv('LOCAL_MODEL_BASE_URL', 'http://localhost:11434')
        self.local_model_name = os.getenv('LOCAL_MODEL_NAME', 'llama2')
        
        # Document processing settings
        self.chunk_size = 1000  # tokens per chunk
        self.chunk_overlap = 100  # reduced overlap for smaller chunks
        
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if self.use_openrouter:
            return bool(self.openrouter_api_key)
        elif self.use_local_model:
            return bool(self.local_model_base_url and self.local_model_name)
        elif self.azure_endpoint:
            return bool(self.azure_api_key and self.azure_deployment)
        else:
            return bool(self.openai_api_key)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for AutoGen agents"""
        if self.use_openrouter:
            return {
                "config_list": [{
                    "model": self.model_name,
                    "api_key": self.openrouter_api_key,
                    "base_url": self.openrouter_base_url
                }],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        elif self.use_local_model:
            return {
                "config_list": [{
                    "model": self.local_model_name,
                    "base_url": self.local_model_base_url,
                    "api_key": "not-needed"
                }],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        elif self.azure_endpoint:
            return {
                "config_list": [{
                    "model": self.model_name,
                    "api_type": "azure",
                    "api_key": self.azure_api_key,
                    "base_url": self.azure_endpoint,
                    "api_version": "2024-02-01",
                    "azure_deployment": self.azure_deployment
                }],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        else:
            return {
                "config_list": [{
                    "model": self.model_name,
                    "api_key": self.openai_api_key,
                }],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get agent-specific configuration"""
        base_config = self.get_llm_config()
        
        # Customize temperature for different agents
        agent_temps = {
            "summary": 0.5,  # More focused for summaries
            "action": 0.3,   # Very precise for action extraction
            "risk": 0.7,     # More creative for risk identification
        }
        
        if agent_name.lower() in agent_temps:
            base_config["temperature"] = agent_temps[agent_name.lower()]
        
        return base_config


# Global config instance
config = Config()
