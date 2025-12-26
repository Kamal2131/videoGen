import os
import json
from rich.console import Console
from src.prompts import get_system_instruction, get_style_defaults
from src.config import Config

console = Console()

# Provider Imports
HAS_GENAI = False
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    pass

HAS_OPENAI = False
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    pass

HAS_GROQ = False
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    pass


class VirtualDirector:
    """
    The 'Brain' that converts scripts into video production sheets.
    Supports: Gemini, OpenAI, Groq.
    """
    
    def __init__(self, style="cinematic", model_name=None, provider="gemini"):
        self.provider = provider.lower()
        self.style = style
        self.style_defaults = get_style_defaults(style)
        self.client = None
        self.model_name = model_name
        self.system_instruction = get_system_instruction(style)
        
        # Initialize Provider
        if self.provider == 'openai':
            self._init_openai(model_name)
        elif self.provider == 'groq':
            self._init_groq(model_name)
        else:
            self._init_gemini(model_name)

    def _init_gemini(self, model_name):
        self.model_name = model_name or "gemini-2.0-flash-exp"
        if HAS_GENAI and Config.GOOGLE_API_KEY:
            try:
                self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
                console.print(f"[green]✓ Director (Gemini): Connected[/green] ({self.model_name})")
            except Exception as e:
                console.print(f"[red]Gemini Error: {e}[/red]")
        else:
            console.print("[yellow]Gemini not available (Missing Key or Lib). Mock Mode active.[/yellow]")

    def _init_openai(self, model_name):
        self.model_name = model_name or "gpt-4-turbo"
        if HAS_OPENAI and Config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                console.print(f"[green]✓ Director (OpenAI): Connected[/green] ({self.model_name})")
            except Exception as e:
                console.print(f"[red]OpenAI Error: {e}[/red]")
        else:
            console.print("[yellow]OpenAI not available (Missing Key or Lib). Mock Mode active.[/yellow]")

    def _init_groq(self, model_name):
        self.model_name = model_name or "llama-3.3-70b-versatile"
        api_key = os.getenv("GROQ_API_KEY")
        if HAS_GROQ and api_key:
            try:
                self.client = Groq(api_key=api_key)
                console.print(f"[green]✓ Director (Groq): Connected[/green] ({self.model_name})")
            except Exception as e:
                console.print(f"[red]Groq Error: {e}[/red]")
        else:
             console.print("[yellow]Groq not available. Mock Mode active.[/yellow]")

    def process_script(self, script_text, target_duration=None):
        """Analyze script and generate scenes."""
        if not self.client:
             return self._mock_response(script_text)

        console.print("[cyan]🎬 Director analyzing script...[/cyan]")
        
        prompt = f"Analyze this story and create a video production sheet:\n\n{script_text}"
        if target_duration:
            prompt += f"\n\nTarget total duration: approximately {target_duration} seconds."
        
        try:
            if self.provider == 'openai':
                scenes = self._generate_with_openai(prompt)
            elif self.provider == 'groq':
                scenes = self._generate_with_groq(prompt)
            else:
                scenes = self._generate_with_gemini(prompt)
            
            return self._post_process_scenes(scenes)
            
        except Exception as e:
            console.print(f"[bold red]Error during generation:[/bold red] {e}")
            return self._mock_response(script_text)

    def _generate_with_gemini(self, prompt):
        # ... (Existing Gemini Logic with relaxed safety)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=self.system_instruction
            )
        )
        return json.loads(response.text)

    def _generate_with_openai(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get('scenes', data) if isinstance(data, dict) else data

    def _generate_with_groq(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return data.get('scenes', data) if isinstance(data, dict) else data

    def _post_process_scenes(self, scenes):
        # Normalize the list
        if isinstance(scenes, dict) and 'scenes' in scenes:
            scenes = scenes['scenes']
            
        for i, scene in enumerate(scenes):
            if 'scene_number' not in scene: scene['scene_number'] = i + 1
            if 'duration_seconds' not in scene: scene['duration_seconds'] = 5
        return scenes

    def _mock_response(self, script_text):
        # Retrieve the deep mock response from before
        return [
            {
                "scene_number": 1, 
                "narrative_beat": "Intro (Mock)", 
                "visual_prompt": "Cinematic shot of a protagonist standing in silence. 4k.",
                "duration_seconds": 5
            }
        ]
