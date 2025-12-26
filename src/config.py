import os
from dotenv import load_dotenv

# Load environment variables once at import time
load_dotenv()

class Config:
    """Central configuration for the VideoGen application."""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # GCP Settings (for Vertex AI)
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
    
    # Application Defaults
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "gemini")
    Video_OUTPUT_DIR = os.getenv("VIDEO_OUTPUT_DIR", "generated_videos")

    @classmethod
    def check_api_key(cls, provider: str) -> bool:
        """Check if API key exists for the given provider."""
        if provider.lower() == "gemini":
            return bool(cls.GOOGLE_API_KEY)
        elif provider.lower() == "openai":
            return bool(cls.OPENAI_API_KEY)
        return False
