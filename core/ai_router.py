"""Smart AI Router for automatic provider fallback."""
import asyncio
import random
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from config.settings import settings
from providers import BaseAIProvider, DeepSeekProvider, GroqProvider, OpenRouterProvider
from .rate_limiter import RateLimiter, QuotaManager


@dataclass
class RouterResult:
    """Result from AI Router."""
    success: bool
    content: str
    provider_used: str
    model_used: str
    tokens_used: Optional[int]
    attempts: int
    errors: List[str]


class AIRouter:
    """Routes requests between AI providers with automatic fallback."""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.rate_limiter = RateLimiter()
        self.quota_manager = QuotaManager()
        self._init_providers()
    
    def _init_providers(self):
        """Initialize all providers."""
        # DeepSeek
        if settings.deepseek_api_key:
            self.providers["deepseek"] = DeepSeekProvider(settings.deepseek_api_key)
        
        # Groq
        if settings.groq_api_key:
            self.providers["groq"] = GroqProvider(settings.groq_api_key)
        
        # OpenRouter
        if settings.openrouter_api_key:
            self.providers["openrouter"] = OpenRouterProvider(settings.openrouter_api_key)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available (configured) provider names."""
        return list(self.providers.keys())
    
    def get_ready_providers(self) -> List[str]:
        """Get list of providers that are ready to use (not rate limited)."""
        ready = []
        for name, provider in self.providers.items():
            if provider.is_available() and not self.rate_limiter.is_rate_limited(name):
                ready.append(name)
        return ready
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "configured": provider.config.api_key is not None,
                "available": provider.is_available(),
                "status": provider.status.value,
                "last_error": provider.last_error,
                "models": provider.available_models
            }
        return status
    
    def _get_provider_priority(self) -> List[str]:
        """Get provider priority list based on availability."""
        ready = self.get_ready_providers()
        
        # Sort by configured priority
        priority = []
        for p in settings.provider_priority:
            if p in ready:
                priority.append(p)
        
        # Add any remaining ready providers
        for p in ready:
            if p not in priority:
                priority.append(p)
        
        return priority
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> RouterResult:
        """Generate content with automatic provider fallback."""
        errors = []
        attempts = 0
        
        # Determine provider order
        if preferred_provider and preferred_provider in self.providers:
            if self.providers[preferred_provider].is_available():
                provider_order = [preferred_provider]
                # Add others as fallback
                for p in self._get_provider_priority():
                    if p != preferred_provider:
                        provider_order.append(p)
            else:
                provider_order = self._get_provider_priority()
        else:
            provider_order = self._get_provider_priority()
        
        if not provider_order:
            return RouterResult(
                success=False,
                content="",
                provider_used="",
                model_used="",
                tokens_used=None,
                attempts=0,
                errors=["No providers available. Please configure at least one API key."]
            )
        
        # Try each provider
        for provider_name in provider_order:
            if attempts >= max_retries:
                break
            
            provider = self.providers.get(provider_name)
            if not provider:
                continue
            
            # Check rate limit
            if self.rate_limiter.is_rate_limited(provider_name):
                wait_time = self.rate_limiter.time_until_available(provider_name)
                if wait_time > 0:
                    errors.append(f"{provider_name}: Rate limited, wait {wait_time:.0f}s")
                    continue
            
            try:
                # Acquire rate limit slot
                await self.rate_limiter.acquire(provider_name)
                
                try:
                    attempts += 1
                    result = await provider.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    if result.success:
                        # Record usage
                        self.quota_manager.record_usage(
                            provider_name,
                            result.tokens_used or 0
                        )
                        
                        return RouterResult(
                            success=True,
                            content=result.content,
                            provider_used=provider_name,
                            model_used=result.model,
                            tokens_used=result.tokens_used,
                            attempts=attempts,
                            errors=errors
                        )
                    else:
                        error_msg = result.error_message or "Unknown error"
                        errors.append(f"{provider_name}: {error_msg}")
                        
                        # Check if rate limited
                        if "rate limit" in error_msg.lower():
                            provider.set_rate_limited()
                            self.rate_limiter.set_rate_limited(provider_name)
                        
                finally:
                    self.rate_limiter.release(provider_name)
                    
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")
                provider.set_error(str(e))
        
        # All providers failed
        return RouterResult(
            success=False,
            content="",
            provider_used="",
            model_used="",
            tokens_used=None,
            attempts=attempts,
            errors=errors
        )
    
    async def generate_with_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Generate content with streaming from the best available provider."""
        # Determine provider
        if preferred_provider and preferred_provider in self.providers:
            if self.providers[preferred_provider].is_available():
                provider_name = preferred_provider
            else:
                ready = self.get_ready_providers()
                if not ready:
                    yield "[Error: No providers available]"
                    return
                provider_name = ready[0]
        else:
            ready = self.get_ready_providers()
            if not ready:
                yield "[Error: No providers available]"
                return
            provider_name = ready[0]
        
        provider = self.providers[provider_name]
        
        try:
            await self.rate_limiter.acquire(provider_name)
            
            try:
                async for chunk in provider.generate_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    yield chunk
                    
            finally:
                self.rate_limiter.release(provider_name)
                
        except Exception as e:
            yield f"[Error: {str(e)}]"
    
    def reset_provider(self, provider_name: str):
        """Reset a provider's status."""
        if provider_name in self.providers:
            self.providers[provider_name].reset_status()
            # Also reset rate limiter
            info = self.rate_limiter.get_limit_info(provider_name)
            info.reset_time = None
            info.requests_remaining = info.requests_limit
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics for all providers."""
        return self.quota_manager.get_all_usage()
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        results = {}
        for name, provider in self.providers.items():
            try:
                results[name] = await provider.check_availability()
            except:
                results[name] = False
        return results
