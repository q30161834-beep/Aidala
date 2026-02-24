"""Main content generation orchestrator."""
from typing import Optional, Dict, Any, AsyncGenerator
import json
from datetime import datetime

from config.prompts import PromptTemplates
from config.settings import settings
from models import AUDIENCES, TONES, CONTENT_TYPES, FRAMEWORKS
from models.audience import get_audience_by_id, create_custom_audience
from models.tone import get_tone_by_id, create_custom_tone
from models.content_types import get_content_type_by_id, create_custom_content_type, create_custom_framework
from .ai_router import AIRouter, RouterResult


class ContentGenerator:
    """Main class for generating marketing content."""
    
    def __init__(self):
        self.router = AIRouter()
        self.history: list[Dict[str, Any]] = []
        self._load_history()
    
    def _load_history(self):
        """Load generation history from file."""
        try:
            if settings.history_file.exists():
                with open(settings.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []
    
    def _save_history(self):
        """Save generation history to file."""
        try:
            with open(settings.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history[-100:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def add_to_history(
        self,
        keywords: str,
        content_type: str,
        framework: str,
        audience: str,
        tone: str,
        result: RouterResult,
        word_count: str = "normal"
    ):
        """Add a generation to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords,
            "content_type": content_type,
            "framework": framework,
            "audience": audience,
            "tone": tone,
            "content": result.content if result.success else None,
            "provider": result.provider_used,
            "success": result.success,
            "tokens": result.tokens_used,
            "word_count": word_count
        }
        self.history.append(entry)
        self._save_history()
    
    def get_history(self, limit: int = 20) -> list[Dict[str, Any]]:
        """Get recent generation history."""
        return self.history[-limit:][::-1]
    
    def clear_history(self):
        """Clear generation history."""
        self.history = []
        self._save_history()
    
    async def generate(
        self,
        keywords: str,
        content_type_id: str,
        framework: str,
        audience_id: str,
        tone_id: str,
        additional_context: str = "",
        preferred_provider: Optional[str] = None,
        word_count: str = "normal",
        custom_audience: Optional[Dict] = None,
        custom_tone: Optional[Dict] = None,
        custom_content_type: Optional[Dict] = None,
        custom_framework: Optional[Dict] = None
    ) -> RouterResult:
        """Generate content based on parameters, with support for custom options."""
        
        # Handle custom audience if provided
        if custom_audience and audience_id.startswith("custom_"):
            audience = create_custom_audience(
                name=custom_audience.get("name", "Custom Audience"),
                description=custom_audience.get("description", "Custom audience description"),
                pain_points=custom_audience.get("pain_points", []),
                desires=custom_audience.get("desires", []),
                objections=custom_audience.get("objections", []),
                language_style=custom_audience.get("language_style", "Casual")
            )
        else:
            audience = get_audience_by_id(audience_id)
        
        # Handle custom tone if provided
        if custom_tone and tone_id.startswith("custom_"):
            tone = create_custom_tone(
                name=custom_tone.get("name", "Custom Tone"),
                description=custom_tone.get("description", "Custom tone description"),
                characteristics=custom_tone.get("characteristics", []),
                examples=custom_tone.get("examples", []),
                best_for=custom_tone.get("best_for", [])
            )
        else:
            tone = get_tone_by_id(tone_id)
        
        # Handle custom content type if provided
        if custom_content_type and content_type_id.startswith("custom_"):
            content_type = create_custom_content_type(
                name=custom_content_type.get("name", "Custom Content Type"),
                description=custom_content_type.get("description", "Custom content type description"),
                optimal_length=custom_content_type.get("optimal_length", "Variable"),
                key_elements=custom_content_type.get("key_elements", []),
                best_practices=custom_content_type.get("best_practices", []),
                platforms=custom_content_type.get("platforms", [])
            )
        else:
            content_type = get_content_type_by_id(content_type_id)
        
        # Handle custom framework if provided
        if custom_framework and framework.startswith("custom_"):
            create_custom_framework(
                name=custom_framework.get("name", "Custom Framework"),
                description=custom_framework.get("description", "Custom framework description"),
                steps=custom_framework.get("steps", []),
                best_for=custom_framework.get("best_for", [])
            )
            # Use the custom framework name in the prompt
            framework = custom_framework.get("name", "Custom Framework")
        
        # Build detailed audience description
        audience_desc = f"""{audience.name}
Descriere: {audience.description}
Pain points: {', '.join(audience.pain_points[:3])}
Dorințe: {', '.join(audience.desires[:3])}
Stil de limbaj preferat: {audience.language_style}"""
        
        # Build detailed tone description
        tone_desc = f"""{tone.name}
Descriere: {tone.description}
Caracteristici: {', '.join(tone.characteristics[:3])}
Exemple: {' | '.join(tone.examples[:2])}"""
        
        # Build prompt
        prompt = PromptTemplates.build_prompt(
            keywords=keywords,
            audience=audience_desc,
            tone=tone_desc,
            content_type=content_type.name,
            framework=framework,
            additional_context=additional_context,
            word_count=word_count
        )
        
        # Add hashtags for Instagram
        if content_type_id == "instagram_caption":
            prompt += "\n\nLa final, adaugă hashtag-uri relevante (15-30)."
        
        # Generate
        result = await self.router.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            preferred_provider=preferred_provider
        )
        
        # Add to history
        self.add_to_history(
            keywords=keywords,
            content_type=content_type.name,
            framework=framework,
            audience=audience.name,
            tone=tone.name,
            result=result,
            word_count=word_count
        )
        
        return result
    
    async def generate_stream(
        self,
        keywords: str,
        content_type_id: str,
        framework: str,
        audience_id: str,
        tone_id: str,
        additional_context: str = "",
        preferred_provider: Optional[str] = None,
        word_count: str = "normal",
        custom_audience: Optional[Dict] = None,
        custom_tone: Optional[Dict] = None,
        custom_content_type: Optional[Dict] = None,
        custom_framework: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming, with support for custom options."""
        
        # Handle custom audience if provided
        if custom_audience and audience_id.startswith("custom_"):
            audience = create_custom_audience(
                name=custom_audience.get("name", "Custom Audience"),
                description=custom_audience.get("description", "Custom audience description"),
                pain_points=custom_audience.get("pain_points", []),
                desires=custom_audience.get("desires", []),
                objections=custom_audience.get("objections", []),
                language_style=custom_audience.get("language_style", "Casual")
            )
        else:
            audience = get_audience_by_id(audience_id)
        
        # Handle custom tone if provided
        if custom_tone and tone_id.startswith("custom_"):
            tone = create_custom_tone(
                name=custom_tone.get("name", "Custom Tone"),
                description=custom_tone.get("description", "Custom tone description"),
                characteristics=custom_tone.get("characteristics", []),
                examples=custom_tone.get("examples", []),
                best_for=custom_tone.get("best_for", [])
            )
        else:
            tone = get_tone_by_id(tone_id)
        
        # Handle custom content type if provided
        if custom_content_type and content_type_id.startswith("custom_"):
            content_type = create_custom_content_type(
                name=custom_content_type.get("name", "Custom Content Type"),
                description=custom_content_type.get("description", "Custom content type description"),
                optimal_length=custom_content_type.get("optimal_length", "Variable"),
                key_elements=custom_content_type.get("key_elements", []),
                best_practices=custom_content_type.get("best_practices", []),
                platforms=custom_content_type.get("platforms", [])
            )
        else:
            content_type = get_content_type_by_id(content_type_id)
        
        # Handle custom framework if provided
        if custom_framework and framework.startswith("custom_"):
            create_custom_framework(
                name=custom_framework.get("name", "Custom Framework"),
                description=custom_framework.get("description", "Custom framework description"),
                steps=custom_framework.get("steps", []),
                best_for=custom_framework.get("best_for", [])
            )
            # Use the custom framework name in the prompt
            framework = custom_framework.get("name", "Custom Framework")
        
        # Build descriptions
        audience_desc = f"""{audience.name} - {audience.description}
Pain points: {', '.join(audience.pain_points[:3])}
Dorințe: {', '.join(audience.desires[:3])}"""
        
        tone_desc = f"""{tone.name} - {tone.description}"""
        
        # Build prompt
        prompt = PromptTemplates.build_prompt(
            keywords=keywords,
            audience=audience_desc,
            tone=tone_desc,
            content_type=content_type.name,
            framework=framework,
            additional_context=additional_context,
            word_count=word_count
        )
        
        if content_type_id == "instagram_caption":
            prompt += "\n\nLa final, adaugă hashtag-uri relevante (15-30)."
        
        # Stream generate
        full_content = []
        async for chunk in self.router.generate_with_stream(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            preferred_provider=preferred_provider
        ):
            full_content.append(chunk)
            yield chunk
        
        # Save to history after streaming completes
        content = "".join(full_content)
        if not content.startswith("[Error"):
            self.add_to_history(
                keywords=keywords,
                content_type=content_type.name,
                framework=framework,
                audience=audience.name,
                tone=tone.name,
                result=RouterResult(
                    success=True,
                    content=content,
                    provider_used="streaming",
                    model_used="unknown",
                    tokens_used=None,
                    attempts=1,
                    errors=[]
                ),
                word_count=word_count
            )
    
    def get_options(self) -> Dict[str, Any]:
        """Get all available options for UI."""
        return {
            "audiences": [
                {"id": a.id, "name": a.name, "description": a.description}
                for a in AUDIENCES
            ],
            "tones": [
                {"id": t.id, "name": t.name, "description": t.description}
                for t in TONES
            ],
            "content_types": [
                {"id": ct.id, "name": ct.name, "description": ct.description}
                for ct in CONTENT_TYPES
            ],
            "frameworks": [
                {
                    "name": name,
                    "description": data["description"],
                    "best_for": data["best_for"]
                }
                for name, data in FRAMEWORKS.items()
            ],
            "providers": self.router.get_available_providers()
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get provider status for UI."""
        return self.router.get_provider_status()
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics."""
        return self.router.get_usage_stats()
    
    async def generate_from_prompt(
        self,
        prompt: str,
        preferred_provider: Optional[str] = None,
        max_tokens: int = 2000
    ) -> RouterResult:
        """Generate content from a custom prompt."""
        result = await self.router.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            preferred_provider=preferred_provider,
            max_tokens=max_tokens
        )
        return result
