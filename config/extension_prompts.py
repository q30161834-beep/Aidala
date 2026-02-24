"""
Prompt templates for content extension/expansion functionality
"""

def build_extension_prompt(initial_content: str, expansion_focus: str = "general") -> str:
    """
    Build a prompt to expand on initial content
    
    Args:
        initial_content: The original content to expand upon
        expansion_focus: The focus area for expansion (general, details, examples, benefits, etc.)
    
    Returns:
        Formatted prompt string for content expansion
    """
    focus_descriptions = {
        "general": "in a general way with more depth and information",
        "details": "by adding more specific details and specifications",
        "examples": "by incorporating relevant examples and case studies",
        "benefits": "by highlighting additional benefits and advantages",
        "features": "by elaborating on key features and characteristics",
        "applications": "by exploring practical applications and use cases",
        "technical": "with more technical depth and specifications",
        "creative": "in a creative and engaging manner with storytelling elements"
    }
    
    focus_description = focus_descriptions.get(expansion_focus, focus_descriptions["general"])
    
    prompt = f"""You are an expert content creator tasked with expanding on the following content:

ORIGINAL CONTENT:
{initial_content}

INSTRUCTIONS:
- Expand the content {focus_description}
- Maintain the original tone and style while adding more depth
- Add relevant information that enhances the original message
- Ensure the expanded content flows naturally from the original
- Keep the core message intact while adding substantial value
- Make the content more comprehensive and informative

EXPANDED CONTENT:"""
    
    return prompt


def build_detailed_expansion_prompt(initial_content: str, expansion_type: str = "comprehensive") -> str:
    """
    Build a detailed expansion prompt with specific expansion requirements
    
    Args:
        initial_content: The original content to expand upon
        expansion_type: Type of expansion (comprehensive, analytical, narrative, etc.)
    
    Returns:
        Detailed expansion prompt
    """
    expansion_types = {
        "comprehensive": "Provide a comprehensive expansion covering all aspects in detail",
        "analytical": "Analyze the content and expand with critical insights and analysis",
        "narrative": "Expand by weaving the content into a compelling narrative",
        "practical": "Focus on practical applications and actionable insights",
        "strategic": "Expand with strategic thinking and business implications",
        "educational": "Expand with educational elements and learning points",
        "persuasive": "Enhance with persuasive elements to convince the audience",
        "creative": "Expand with creative flair and innovative perspectives"
    }
    
    type_instruction = expansion_types.get(expansion_type, expansion_types["comprehensive"])
    
    prompt = f"""You are a skilled content developer. Your task is to expand the following content:

INITIAL CONTENT:
{initial_content}

EXPANSION REQUIREMENTS:
{type_instruction}

SPECIFIC DIRECTIONS:
- Preserve the original message and intent
- Add substantial new value and insights
- Structure the expanded content logically
- Enhance readability and engagement
- Incorporate relevant examples where appropriate
- Maintain consistency with the original style

OUTPUT:
Please provide the expanded content that builds upon the initial piece while adding significant value."""
    
    return prompt