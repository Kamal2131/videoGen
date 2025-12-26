from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class VideoGenerator(ABC):
    """Abstract base class for video generation providers."""
    
    @abstractmethod
    def generate_scene_video(self, scene: Dict, output_dir: str) -> Optional[str]:
        """Generate a single video for a scene."""
        pass
    
    @abstractmethod
    def generate_batch(self, scenes: List[Dict], output_dir: str, parallel_count: int = 2) -> List[str]:
        """Generate videos for multiple scenes."""
        pass
