from .gemini_veo import GeminiVeoGenerator
from .openai_sora import OpenAISoraGenerator

def get_video_generator(provider: str):
    """Factory to get the video generator instance."""
    p = provider.lower()
    if p == 'openai':
        return OpenAISoraGenerator()
    elif p == 'gemini':
        return GeminiVeoGenerator()
    else:
        # Default to Gemini/Veo
        return GeminiVeoGenerator()
