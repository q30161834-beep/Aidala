"""Base class for AI providers."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class ProviderStatus(Enum):
    """Provider status."""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class GenerationResult:
    """Result from content generation."""
    success: bool
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    api_key: Optional[str]
    base_url: str
    default_model: str
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 60


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.status = ProviderStatus.AVAILABLE if config.api_key else ProviderStatus.DISABLED
        self.last_error: Optional[str] = None
        self.rate_limit_reset: Optional[float] = None
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """Return list of available models."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GenerationResult:
        """Generate content from prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming."""
        pass
    
    @abstractmethod
    async def check_availability(self) -> bool:
        """Check if provider is available."""
        pass
    
    def is_available(self) -> bool:
        """Check if provider can be used."""
        if not self.config.api_key:
            return False
        if self.status == ProviderStatus.DISABLED:
            return False
        if self.status == ProviderStatus.RATE_LIMITED:
            import time
            if self.rate_limit_reset and time.time() < self.rate_limit_reset:
                return False
            self.status = ProviderStatus.AVAILABLE
        return self.status == ProviderStatus.AVAILABLE
    
    def set_rate_limited(self, reset_time: Optional[float] = None):
        """Mark provider as rate limited."""
        self.status = ProviderStatus.RATE_LIMITED
        self.rate_limit_reset = reset_time
    
    def set_error(self, error_message: str):
        """Mark provider as having an error."""
        self.status = ProviderStatus.ERROR
        self.last_error = error_message
    
    def reset_status(self):
        """Reset provider status to available."""
        if self.config.api_key:
            self.status = ProviderStatus.AVAILABLE
        else:
            self.status = ProviderStatus.DISABLED
        self.last_error = None
        self.rate_limit_reset = None
    
    def _get_model(self, model: Optional[str]) -> str:
        """Get model name, falling back to default."""
        return model or self.config.default_model
    
    def _get_temperature(self, temperature: Optional[float]) -> float:
        """Get temperature, falling back to default."""
        return temperature if temperature is not None else self.config.temperature
    
    def _get_max_tokens(self, max_tokens: Optional[int]) -> int:
        """Get max tokens, falling back to default."""
        return max_tokens if max_tokens is not None else self.config.max_tokens
