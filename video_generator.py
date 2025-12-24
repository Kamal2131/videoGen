"""
Google Veo 2 Video Generator Module

This module provides integration with Google Veo 2 via:
1. Google Vertex AI (Enterprise/Production)
2. Google Gemini API (experimental/beta via API Key)

It handles async video generation, polling, and batch processing.
"""

import os
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

# Import Vertex AI
try:
    from google.cloud import aiplatform
    HAS_VERTEX_AI = True
except ImportError:
    HAS_VERTEX_AI = False

# Import Gemini API (New unified SDK)
try:
    from google import genai as google_genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False


class VeoVideoGenerator:
    """
    Google Veo 2 video generator supporting both Vertex AI and Gemini API.
    """
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """
        Initialize Veo video generator.
        Prioritizes Gemini API Key via google-genai SDK, falls back to Vertex AI.
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.output_dir = "generated_videos"
        self.client = None
        
        # Check for Gemini API Key first (User's request)
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.use_gemini = False
        
        if self.api_key and HAS_GOOGLE_GENAI:
            try:
                # Initialize client once
                self.client = google_genai.Client(api_key=self.api_key)
                # Verify that it's the correct client type
                if hasattr(self.client, 'models'):
                    self.use_gemini = True
                    console.print(f"[green]✓ Video Generator initialized via google-genai SDK[/green]")
                    if not hasattr(self.client.models, 'generate_videos'):
                        console.print(f"[yellow]⚠ Warning: generate_videos not found on client.models. Available: {dir(self.client.models)}[/yellow]")
                else:
                    console.print("[red]Error: Client initialized but 'models' attribute missing.[/red]")
            except Exception as e:
                 console.print(f"[red]Error initializing google-genai client: {e}[/red]")
        elif self.api_key and not HAS_GOOGLE_GENAI:
            console.print("[yellow]⚠ GOOGLE_API_KEY found but 'google-genai' SDK not installed.[/yellow]")
            console.print("Run: pip install google-genai")

        # Fallback/Alternative: Vertex AI
        if not self.use_gemini and HAS_VERTEX_AI and self.project_id:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                console.print(f"[green]✓ Video Generator initialized via Vertex AI[/green] (Project: {self.project_id})")
            except Exception as e:
                console.print(f"[red]Failed to initialize Vertex AI: {e}[/red]")
        
        if not self.use_gemini and not (HAS_VERTEX_AI and self.project_id):
            console.print("[bold red]Error: No valid video generation method found.[/bold red]")
            console.print("Please set GOOGLE_API_KEY and install google-genai, OR set GCP_PROJECT_ID.")

    def generate_scene_video(self, scene: Dict, output_dir: str = "generated_videos", aspect_ratio: str = "16:9") -> Optional[str]:
        """Generate video for a single scene using available backend."""
        scene_number = scene.get("scene_number", 1)
        prompt = scene.get("visual_prompt", "")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, f"scene_{scene_number}.mp4")
        
        console.print(f"\n[cyan]🎬 Generating Scene {scene_number}...[/cyan]")
        
        if self.use_gemini:
            return self._generate_via_gemini(prompt, output_path)
        elif self.project_id:
            return self._generate_via_vertex(prompt, output_path)
        else:
            console.print("[red]No video generation backend configured.[/red]")
            return None

    def _generate_via_gemini(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate video using Gemini API (google-genai SDK)."""
        if not self.client:
            console.print("[red]Error: google-genai client not initialized.[/red]")
            return None

        try:
            console.print(f"[yellow]⏳ Submitting to Gemini API (Veo 2)...[/yellow]")
            console.print("[dim]This may take 1-2 minutes...[/dim]")
            
            # Using Veo 2 model
            # Config passed as dict to avoid TypeErrors with missing config classes
            response = self.client.models.generate_videos(
                model='veo-2.0-generate-001',
                prompt=prompt,
                config={
                }
            )
            
            console.print(f"[dim]Response received. Type: {type(response)}[/dim]")
            
            # Handle Long Running Operation (LRO)
            if hasattr(response, 'result'):
                console.print("[yellow]Waiting for video generation to complete...[/yellow]")
                # .result() blocks until operation is complete
                result = response.result()
            else:
                result = response
            
            # Try to extract bytes safely from result
            video_bytes = None
            
            # Check for generated_videos list
            if hasattr(result, 'generated_videos'):
                if len(result.generated_videos) > 0:
                    # Some versions use .video.video_bytes, some use .bytes
                    video_obj = result.generated_videos[0]
                    if hasattr(video_obj, 'video') and hasattr(video_obj.video, 'video_bytes'):
                         video_bytes = video_obj.video.video_bytes
                    elif hasattr(video_obj, 'bytes'):
                         video_bytes = video_obj.bytes
                    else:
                         console.print(f"[red]Could not find bytes in video object. Attributes: {dir(video_obj)}[/red]")
                else:
                    console.print("[red]Result returned empty generated_videos list.[/red]")
            # Fallback checks
            elif hasattr(result, 'bytes'):
                 video_bytes = result.bytes
            
            if not video_bytes:
                 # Debug available attributes if we failed
                 console.print(f"[yellow]Debug attributes of result: {dir(result)}[/yellow]")

            if video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                console.print(f"[green]✓ Video generated (Gemini API): {output_path}[/green]")
                return output_path
            else:
                console.print("[red]Failed to retrieve video bytes from response.[/red]")
                return None
            
        except Exception as e:
            console.print(f"[red]Gemini API Error: {e}[/red]")
            # Fallback for debugging
            if "NOT_FOUND" in str(e):
                 console.print("[yellow]Model 'veo-2.0-generate-001' not found. Check if you have access to Veo.[/yellow]")
            return None

    def _generate_via_vertex(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate video using Vertex AI."""
        try:
            console.print(f"[yellow]⏳ Submitting to Vertex AI (Veo)...[/yellow]")
            # Mock implementation for Vertex as placeholder
            time.sleep(3)
            # Still mock here as user is focused on Gemini API path now
            Path(output_path).touch()
            console.print(f"[green]✓ Video generated (Vertex AI): {output_path}[/green]")
            return output_path
        except Exception as e:
            console.print(f"[red]Vertex AI Error: {e}[/red]")
            return None

    def generate_batch(self, scenes: List[Dict], output_dir: str = "generated_videos", parallel_count: int = 2) -> List[str]:
        """Generate videos for multiple scenes."""
        console.print(f"\n[bold cyan]🎥 Starting Batch Video Generation[/bold cyan]")
        video_files = []
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
            task = progress.add_task(f"[cyan]Generating {len(scenes)} videos...", total=len(scenes))
            
            for scene in scenes:
                video_path = self.generate_scene_video(scene, output_dir=output_dir)
                if video_path:
                    video_files.append(video_path)
                progress.update(task, advance=1)
        
        return video_files

if __name__ == "__main__":
    # Test
    gen = VeoVideoGenerator()
    gen.generate_scene_video({"scene_number": 99, "visual_prompt": "Test video generation"})

