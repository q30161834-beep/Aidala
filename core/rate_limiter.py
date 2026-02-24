"""Rate limiting and quota management."""
import time
import asyncio
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RateLimitInfo:
    """Rate limit information for a provider."""
    requests_remaining: int = 100
    requests_limit: int = 100
    tokens_remaining: int = 10000
    tokens_limit: int = 10000
    reset_time: Optional[float] = None
    last_request_time: float = field(default_factory=time.time)
    request_count: int = 0
    
    def is_rate_limited(self) -> bool:
        """Check if currently rate limited."""
        if self.reset_time and time.time() < self.reset_time:
            return True
        if self.requests_remaining <= 0:
            return True
        return False
    
    def time_until_reset(self) -> float:
        """Get seconds until rate limit resets."""
        if not self.reset_time:
            return 0
        return max(0, self.reset_time - time.time())


class RateLimiter:
    """Manages rate limits across multiple providers."""
    
    def __init__(self):
        self._limits: Dict[str, RateLimitInfo] = defaultdict(RateLimitInfo)
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._default_max_requests = 10  # requests per minute default
        self._default_min_interval = 6.0  # seconds between requests
    
    def get_limit_info(self, provider_name: str) -> RateLimitInfo:
        """Get rate limit info for a provider."""
        return self._limits[provider_name]
    
    def update_from_headers(
        self,
        provider_name: str,
        headers: Dict[str, str]
    ):
        """Update rate limits from HTTP response headers."""
        info = self._limits[provider_name]
        
        # Common header patterns
        if "x-ratelimit-remaining" in headers:
            info.requests_remaining = int(headers["x-ratelimit-remaining"])
        if "x-ratelimit-limit" in headers:
            info.requests_limit = int(headers["x-ratelimit-limit"])
        if "x-ratelimit-reset" in headers:
            info.reset_time = float(headers["x-ratelimit-reset"])
        
        # Groq specific
        if "x-ratelimit-remaining-requests" in headers:
            info.requests_remaining = int(headers["x-ratelimit-remaining-requests"])
        if "x-ratelimit-limit-requests" in headers:
            info.requests_limit = int(headers["x-ratelimit-limit-requests"])
        if "x-ratelimit-reset-requests" in headers:
            info.reset_time = time.time() + int(headers["x-ratelimit-reset-requests"])
        
        info.last_request_time = time.time()
        info.request_count += 1
    
    def set_rate_limited(self, provider_name: str, reset_after: Optional[float] = None):
        """Mark a provider as rate limited."""
        info = self._limits[provider_name]
        info.requests_remaining = 0
        if reset_after:
            info.reset_time = time.time() + reset_after
    
    def is_rate_limited(self, provider_name: str) -> bool:
        """Check if a provider is currently rate limited."""
        return self._limits[provider_name].is_rate_limited()
    
    def time_until_available(self, provider_name: str) -> float:
        """Get seconds until provider is available again."""
        return self._limits[provider_name].time_until_reset()
    
    async def acquire(self, provider_name: str):
        """Acquire permission to make a request."""
        # Initialize semaphore if needed
        if provider_name not in self._semaphores:
            self._semaphores[provider_name] = asyncio.Semaphore(self._default_max_requests)
        
        semaphore = self._semaphores[provider_name]
        info = self._limits[provider_name]
        
        # Wait if rate limited
        while self.is_rate_limited(provider_name):
            wait_time = self.time_until_available(provider_name)
            if wait_time > 0:
                await asyncio.sleep(min(wait_time, 60))  # Max 60 second wait
            else:
                # Reset if no specific reset time
                info.requests_remaining = info.requests_limit
                info.reset_time = None
                break
        
        # Acquire semaphore with timeout
        try:
            await asyncio.wait_for(
                semaphore.acquire(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            raise Exception(f"Could not acquire rate limit slot for {provider_name}")
        
        # Enforce minimum interval between requests
        time_since_last = time.time() - info.last_request_time
        if time_since_last < self._default_min_interval:
            await asyncio.sleep(self._default_min_interval - time_since_last)
    
    def release(self, provider_name: str):
        """Release a request slot."""
        if provider_name in self._semaphores:
            try:
                self._semaphores[provider_name].release()
            except ValueError:
                # Semaphore was already at max value
                pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass


class QuotaManager:
    """Manages usage quotas across providers."""
    
    def __init__(self):
        self._daily_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._last_reset: float = time.time()
    
    def _check_reset(self):
        """Check if daily quotas should be reset."""
        current_time = time.time()
        seconds_in_day = 24 * 60 * 60
        
        if current_time - self._last_reset > seconds_in_day:
            self._daily_usage.clear()
            self._last_reset = current_time
    
    def record_usage(self, provider_name: str, tokens: int = 0):
        """Record usage for a provider."""
        self._check_reset()
        self._daily_usage[provider_name]["requests"] += 1
        self._daily_usage[provider_name]["tokens"] += tokens
    
    def get_usage(self, provider_name: str) -> Dict[str, int]:
        """Get usage statistics for a provider."""
        self._check_reset()
        return dict(self._daily_usage[provider_name])
    
    def get_all_usage(self) -> Dict[str, Dict[str, int]]:
        """Get usage for all providers."""
        self._check_reset()
        return {k: dict(v) for k, v in self._daily_usage.items()}
    
    def estimate_cost(self, provider_name: str, tokens: int) -> float:
        """Estimate cost for tokens (rough estimates)."""
        # Rough pricing estimates per 1K tokens (input + output)
        pricing = {
            "google_ai": 0.0,  # Free tier
            "groq": 0.0,       # Free tier available
            "openrouter": 0.0  # Depends on model, free tier available
        }
        
        rate = pricing.get(provider_name, 0.0)
        return (tokens / 1000) * rate
