"""Configurare implicita pentru CopySpell AI"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """Configurari implicite - fara API keys sensibile"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Keys - vor fi completate de utilizator
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    
    # App Settings
    app_name: str = "CopySpell AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Rate Limiting
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 60
    
    # Provider Priority (order of fallback)
    provider_priority: list[str] = Field(default=["groq", "deepseek", "openrouter"])
    
    @property
    def config_dir(self) -> Path:
        """Get configuration directory."""
        config_path = Path.home() / ".copyspell-ai"
        config_path.mkdir(exist_ok=True)
        return config_path

    @property
    def history_file(self) -> Path:
        """Get history file path."""
        return self.config_dir / "history.json"

    def save_api_keys(self):
        """Save API keys to .env file."""
        env_path = Path(".env")
        env_content = []
        
        if env_path.exists():
            env_content = env_path.read_text().splitlines()
        
        # Update or add API keys
        keys_to_save = {
            "DEEPSEEK_API_KEY": self.deepseek_api_key or "",
            "GROQ_API_KEY": self.groq_api_key or "",
            "OPENROUTER_API_KEY": self.openrouter_api_key or ""
        }
        
        existing_keys = set()
        for i, line in enumerate(env_content):
            for key in keys_to_save:
                if line.startswith(f"{key}="):
                    env_content[i] = f"{key}={keys_to_save[key]}"
                    existing_keys.add(key)
        
        for key, value in keys_to_save.items():
            if key not in existing_keys:
                env_content.append(f"{key}={value}")
        
        env_path.write_text("\n".join(env_content))

    def has_any_api_key(self) -> bool:
        """Check if at least one API key is configured."""
        return any([
            self.deepseek_api_key,
            self.groq_api_key,
            self.openrouter_api_key
        ])


# Global settings instance
default_settings = DefaultSettings()