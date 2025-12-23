import os
import json
from rich.console import Console
from prompts import get_system_instruction, get_style_defaults

console = Console()

# Try to import Gemini, fallback if not available
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    console.print("[bold yellow]Note:[/bold yellow] 'google-generativeai' library not found. Running in offline MOCK MODE.")


class VirtualDirector:
    """
    Enhanced Virtual Director with Flow-specific optimizations.
    
    Features:
    - Flow-optimized prompt engineering
    - Character consistency tracking
    - Multiple style presets
    - Enhanced scene structure
    """
    
    def __init__(self, api_key=None, style="cinematic", model_name='gemini-2.0-flash-exp'):
        """
        Initialize the Virtual Director.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            style: Style preset ('cinematic', 'documentary', 'commercial', 'artistic', 'anime')
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.style = style
        self.style_defaults = get_style_defaults(style)
        self.character_profiles = {}
        
        if HAS_GENAI and self.api_key:
            genai.configure(api_key=self.api_key)
            system_instruction = get_system_instruction(style)
            
            try:
                self.model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_instruction
                )
                console.print(f"[green]✓ Virtual Director ready[/green] (Model: {model_name}, Style: {style})")
            except Exception as e:
                console.print(f"[yellow]Could not initialize {model_name}: {e}[/yellow]")
                console.print("[yellow]Trying fallback model: gemini-1.5-flash[/yellow]")
                try:
                    self.model = genai.GenerativeModel(
                        'gemini-1.5-flash',
                        system_instruction=system_instruction
                    )
                    console.print(f"[green]✓ Virtual Director ready[/green] (Model: gemini-1.5-flash, Style: {style})")
                except Exception as e2:
                    console.print(f"[red]Failed to initialize model: {e2}[/red]")
                    self.model = None
        else:
            self.model = None
            if not HAS_GENAI:
                console.print("[yellow]Virtual Director running in OFFLINE MOCK MODE (Library missing).[/yellow]")
            else:
                console.print("[bold red]Warning:[/bold red] No API Key found. Running in [bold yellow]MOCK MODE[/bold yellow].")

    def process_script(self, script_text, target_duration=None):
        """
        Process the script and generate Flow-optimized video prompts.
        
        Args:
            script_text: The story/script to convert
            target_duration: Optional target duration in seconds
        
        Returns:
            List of scene dictionaries with enhanced metadata
        """
        if not self.model:
            return self._mock_response(script_text)

        console.print("[cyan]🎬 Director analyzing script...[/cyan]")
        
        # Build the prompt with optional duration guidance
        prompt = f"Analyze this story and create a video production sheet:\n\n{script_text}"
        
        if target_duration:
            prompt += f"\n\nTarget total duration: approximately {target_duration} seconds. Adjust scene count accordingly."
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            scenes = json.loads(response.text)
            
            # Post-process scenes to ensure completeness
            scenes = self._post_process_scenes(scenes)
            
            console.print(f"[green]✓ Generated {len(scenes)} scenes[/green]")
            return scenes
            
        except Exception as e:
            console.print(f"[bold red]Error during generation:[/bold red] {e}")
            console.print("[yellow]Falling back to mock output.[/yellow]")
            return self._mock_response(script_text)

    def _post_process_scenes(self, scenes):
        """
        Ensure all scenes have required fields and apply defaults.
        """
        for i, scene in enumerate(scenes):
            # Ensure scene number
            if 'scene_number' not in scene:
                scene['scene_number'] = i + 1
            
            # Set defaults for missing fields
            if 'duration_seconds' not in scene:
                scene['duration_seconds'] = 5  # Default duration
            
            if 'transition_type' not in scene:
                scene['transition_type'] = 'cut' if i < len(scenes) - 1 else 'fade'
            
            if 'motion_intensity' not in scene:
                scene['motion_intensity'] = 'medium'
            
            if 'key_elements' not in scene:
                scene['key_elements'] = []
            
            if 'audio_suggestion' not in scene:
                scene['audio_suggestion'] = 'Ambient atmosphere'
        
        return scenes

    def _mock_response(self, script_text):
        """
        Enhanced mock response with all new fields.
        """
        return [
            {
                "scene_number": 1,
                "narrative_beat": "लड़का छत पर तारों को देख रहा है (Mock Output)",
                "visual_prompt": "Wide establishing shot: A young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, sits cross-legged on a terracotta rooftop. The night sky above is filled with countless twinkling stars. Ancient village houses visible in background. 35mm lens, deep focus, 4K resolution, cinematic composition, dreamy atmosphere.",
                "camera_movement": "Slow crane shot ascending, 35mm lens",
                "mood_lighting": "Soft moonlight, cool blue tones 5600K, starlight highlights",
                "duration_seconds": 6,
                "transition_type": "dissolve",
                "motion_intensity": "low",
                "key_elements": ["boy on rooftop", "starry sky", "village backdrop"],
                "audio_suggestion": "Gentle night crickets, distant village sounds, soft ambient music"
            },
            {
                "scene_number": 2,
                "narrative_beat": "आसमान से रहस्यमय रोशनी आती है (Mock Output)",
                "visual_prompt": "Medium close-up: The same young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, looks upward with widening eyes. Suddenly, an intensely bright white orb of light descends from the clouds above, leaving a shimmering trail. The light reflects in his eyes. 50mm portrait lens, shallow depth of field, high dynamic range, volumetric lighting, hyper-realistic texture.",
                "camera_movement": "Quick tilt up following the light, then zoom in on boy's face, 50mm lens",
                "mood_lighting": "Dramatic contrast: dark night interrupted by brilliant white light source, rim lighting on boy's face",
                "duration_seconds": 5,
                "transition_type": "cut",
                "motion_intensity": "high",
                "key_elements": ["descending light orb", "boy's reaction", "light trail"],
                "audio_suggestion": "Ethereal whooshing sound, rising tension music, boy's breath"
            },
            {
                "scene_number": 3,
                "narrative_beat": "रोशनी परी में बदलती है (Mock Output)",
                "visual_prompt": "Slow motion shot: The bright orb hovers in front of the young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts. The light transforms, revealing a tiny ethereal fairy with translucent dragonfly wings, glowing with soft iridescent light. She extends a delicate hand toward the boy. Anamorphic 2.39:1, bokeh background, magical particles, 8K detail, cinematic color grade with teal and gold tones.",
                "camera_movement": "Circular tracking shot around the transformation, slow push-in, anamorphic lens",
                "mood_lighting": "Soft internal glow from fairy casting warm 3200K light, magical atmosphere",
                "duration_seconds": 7,
                "transition_type": "match_cut",
                "motion_intensity": "medium",
                "key_elements": ["light transformation", "fairy appearance", "outstretched hand"],
                "audio_suggestion": "Magical chimes, soft ethereal vocals, transformation sound effect"
            }
        ]

    def get_statistics(self, scenes):
        """
        Calculate statistics about the generated scenes.
        
        Args:
            scenes: List of scene dictionaries
        
        Returns:
            Dictionary with statistics
        """
        if not scenes:
            return {}
        
        total_duration = sum(s.get('duration_seconds', 5) for s in scenes)
        
        motion_counts = {}
        for scene in scenes:
            motion = scene.get('motion_intensity', 'unknown')
            motion_counts[motion] = motion_counts.get(motion, 0) + 1
        
        return {
            'total_scenes': len(scenes),
            'total_duration': total_duration,
            'average_scene_duration': total_duration / len(scenes),
            'motion_distribution': motion_counts
        }
