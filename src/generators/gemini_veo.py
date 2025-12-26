import os
import time
from typing import List, Dict, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from .base import VideoGenerator
from ..config import Config

console = Console()

class GeminiVeoGenerator(VideoGenerator):
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        self.client = None
        
        # Initialize Google GenAI Client
        try:
            from google import genai
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                console.print("[green]✓ Video Generator (Veo): Initialized[/green]")
            else:
                 console.print("[yellow]⚠ Video Generator (Veo): No API Key found.[/yellow]")
        except ImportError:
            console.print("[red]Error: google-genai library missing.[/red]")

    def generate_scene_video(self, scene: Dict, output_dir: str) -> Optional[str]:
        if not self.client:
            return None
            
        scene_number = scene.get("scene_number", 1)
        prompt = scene.get("visual_prompt", "")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, f"scene_{scene_number}.mp4")
        
        console.print(f"[cyan]🎬 Generating Scene {scene_number} (Veo)...[/cyan]")
        
        try:
            response = self.client.models.generate_videos(
                model='veo-2.0-generate-001', # or 'veo-3.1-generate-preview'
                prompt=prompt
            )
            
            # Wait for LRO
            if hasattr(response, 'result'):
                result = response.result()
            else:
                result = response
                
            # Extract Bytes (Simplified logic vs original)
            video_bytes = None
            if hasattr(result, 'generated_videos') and result.generated_videos:
                vid = result.generated_videos[0]
                video_bytes = getattr(vid.video, 'video_bytes', getattr(vid, 'bytes', None))
            elif hasattr(result, 'bytes'):
                video_bytes = result.bytes
                
            if video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                console.print(f"[green]✓ Saved: {output_path}[/green]")
                return output_path
            else:
                console.print(f"[red]Failed to get video bytes for Scene {scene_number}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]Veo Error Scene {scene_number}: {e}[/red]")
            return None

    def generate_batch(self, scenes: List[Dict], output_dir: str, parallel_count: int = 2) -> List[str]:
        """Sequential generation for simplicity in this refactor."""
        generated = []
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
            task = progress.add_task(f"[cyan]Processing {len(scenes)} scenes...", total=len(scenes))
            for scene in scenes:
                path = self.generate_scene_video(scene, output_dir)
                if path: generated.append(path)
                progress.advance(task)
        return generated
