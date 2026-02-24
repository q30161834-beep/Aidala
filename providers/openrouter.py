"""OpenRouter provider implementation."""
import json
from typing import Optional, AsyncGenerator
import httpx

from .base import BaseAIProvider, ProviderConfig, GenerationResult


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter provider - access to multiple models."""
    
    API_BASE = "https://openrouter.ai/api/v1"
    
    DEFAULT_MODELS = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        "meta-llama/llama-3.3-70b-instruct",
        "google/gemini-pro-1.5",
        "mistralai/mistral-7b-instruct",
    ]
    
    def __init__(self, api_key: Optional[str]):
        config = ProviderConfig(
            name="openrouter",
            api_key=api_key,
            base_url=self.API_BASE,
            default_model="anthropic/claude-3.5-sonnet",
            max_tokens=2048,
            temperature=0.7
        )
        super().__init__(config)
    
    @property
    def provider_name(self) -> str:
        return "OpenRouter"
    
    @property
    def available_models(self) -> list[str]:
        return self.DEFAULT_MODELS
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GenerationResult:
        """Generate content using OpenRouter."""
        if not self.config.api_key:
            return GenerationResult(
                success=False,
                content="",
                provider=self.provider_name,
                model="",
                error_message="API key not configured"
            )
        
        model_name = self._get_model(model)
        temp = self._get_temperature(temperature)
        max_tok = self._get_max_tokens(max_tokens)
        
        url = f"{self.API_BASE}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tok,
            "top_p": 0.95,
            "stream": False,
            "transforms": ["middle-out"]  # OpenRouter feature for context window
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://copyspell-ai.app",
            "X-Title": "CopySpell AI"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 429:
                    error_data = response.json() if response.text else {}
                    retry_after = error_data.get("error", {}).get("metadata", {}).get("retry_after")
                    reset_time = None
                    if retry_after:
                        import time
                        reset_time = time.time() + retry_after
                    self.set_rate_limited(reset_time)
                    return GenerationResult(
                        success=False,
                        content="",
                        provider=self.provider_name,
                        model=model_name,
                        error_message="Rate limit exceeded"
                    )
                
                # Check for provider-specific errors
                if response.status_code == 402:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", {}).get("message", "Insufficient credits")
                    return GenerationResult(
                        success=False,
                        content="",
                        provider=self.provider_name,
                        model=model_name,
                        error_message=error_msg
                    )
                
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data.get("usage", {}).get("total_tokens")
                    
                    return GenerationResult(
                        success=True,
                        content=content,
                        provider=self.provider_name,
                        model=model_name,
                        tokens_used=tokens_used,
                        raw_response=data
                    )
                
                return GenerationResult(
                    success=False,
                    content="",
                    provider=self.provider_name,
                    model=model_name,
                    error_message="No content in response"
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except:
                pass
            
            if e.response.status_code == 429:
                self.set_rate_limited()
                error_msg = "Rate limit exceeded"
            
            self.set_error(error_msg)
            return GenerationResult(
                success=False,
                content="",
                provider=self.provider_name,
                model=model_name,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.set_error(error_msg)
            return GenerationResult(
                success=False,
                content="",
                provider=self.provider_name,
                model=model_name,
                error_message=error_msg
            )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming."""
        model_name = self._get_model(model)
        temp = self._get_temperature(temperature)
        max_tok = self._get_max_tokens(max_tokens)
        
        url = f"{self.API_BASE}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tok,
            "top_p": 0.95,
            "stream": True,
            "transforms": ["middle-out"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://copyspell-ai.app",
            "X-Title": "CopySpell AI"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status_code == 429:
                        self.set_rate_limited()
                        yield "[Rate limit exceeded]"
                        return
                    
                    if response.status_code == 402:
                        yield "[Insufficient credits]"
                        return
                    
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {str(e)}]"
    
    async def check_availability(self) -> bool:
        """Check if OpenRouter is available."""
        if not self.config.api_key:
            return False
        
        try:
            url = f"{self.API_BASE}/auth/key"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                return response.status_code == 200
        except:
            return False
    
    async def get_credits(self) -> Optional[dict]:
        """Get remaining credits info."""
        if not self.config.api_key:
            return None
        
        try:
            url = f"{self.API_BASE}/auth/key"
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", {})
        except:
            pass
        return None
