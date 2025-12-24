import os
import json
from rich.console import Console
from prompts import get_system_instruction, get_style_defaults

console = Console()

# Try to import Gemini, fallback if not available
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    console.print("[bold yellow]Note:[/bold yellow] 'google-genai' library not found.")

# ... (Groq import remains same)

class VirtualDirector:
    # ... (init docstring same)
    
    def __init__(self, api_key=None, style="cinematic", model_name='gemini-2.0-flash-exp', provider='gemini'):
        # ... (provider, api_key logic same)
        self.provider = provider.lower()
        if self.provider == 'gemini':
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        else:
            self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.style = style
        self.style_defaults = get_style_defaults(style)
        self.character_profiles = {}
        self.client = None
        self.model_name = model_name
        
        # Initialize based on provider
        if self.provider == 'groq':
            self._init_groq(model_name, style)
        else:  # default to gemini
            self._init_gemini(model_name, style)
    
    def _init_gemini(self, model_name, style):
        """Initialize Gemini provider (Google GenAI V2)."""
        if HAS_GENAI and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.system_instruction = get_system_instruction(style)
                console.print(f"[green]✓ Virtual Director ready[/green] (Provider: Gemini V2, Model: {model_name}, Style: {style})")
            except Exception as e:
                console.print(f"[red]Failed to initialize Gemini Client: {e}[/red]")
                self.client = None
        else:
            if not HAS_GENAI:
                console.print("[yellow]google-genai library not installed. Running in MOCK MODE.[/yellow]")
            else:
                console.print("[bold red]Warning:[/bold red] No GOOGLE_API_KEY found. Running in [bold yellow]MOCK MODE[/bold yellow].")
    
    # ... (Groq init same)

    def process_script(self, script_text, target_duration=None):
        # ... (docstring same)
        
        if self.provider == 'gemini' and not self.client:
             return self._mock_response(script_text)
        elif self.provider == 'groq' and not self.model: # Groq uses self.model
             return self._mock_response(script_text)

        console.print("[cyan]🎬 Director analyzing script...[/cyan]")
        
        # Build the prompt with optional duration guidance
        prompt = f"Analyze this story and create a video production sheet:\n\n{script_text}"
        
        if target_duration:
            prompt += f"\n\nTarget total duration: approximately {target_duration} seconds. Adjust scene count accordingly."
        
        try:
            if self.provider == 'groq':
                scenes = self._generate_with_groq(prompt)
            else:
                scenes = self._generate_with_gemini(prompt)
            
            # Post-process scenes to ensure completeness
            scenes = self._post_process_scenes(scenes)
            
            console.print(f"[green]✓ Generated {len(scenes)} scenes[/green]")
            return scenes
            
        except Exception as e:
            console.print(f"[bold red]Error during generation:[/bold red] {e}")
            console.print("[yellow]Falling back to mock output.[/yellow]")
            return self._mock_response(script_text)
    
    def _generate_with_gemini(self, prompt):
        """Generate with Gemini API (GenAI V2)."""
        # Loosening safety settings for creative storytelling
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
        ]
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                safety_settings=safety_settings,
                system_instruction=self.system_instruction
            )
        )
        
        if not response.text:
             raise Exception(f"No content returned. Finish Reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")

        return json.loads(response.text)
    
    def _generate_with_groq(self, prompt):
        """Generate with Groq API."""
        system_instruction = get_system_instruction(self.style)
        
        response = self.model.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Groq returns JSON but might wrap it differently
        if isinstance(data, dict) and 'scenes' in data:
            return data['scenes']
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unexpected Groq response format: {data}")

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
        Enhanced mock response with ULTRA-DEPTH demonstrating scene interlinking and character micro-behavior.
        """
        return [
            {
                "scene_number": 1,
                "narrative_beat": "लड़का छत पर तारों को देख रहा है (Mock Output)",
                "visual_prompt": "[SETTING ANCHOR: Moonlit rooftop in a quiet Indian village, midnight]. [SUBJECT: Raju, a 10-year-old Indian boy, wearing a faded blue cotton shirt and dark shorts, skin sun-tanned]. [ACTION & MOVEMENT: He sits cross-legged, weight shifted slightly onto his left hip. His shoulders are dropped, breathing so slowly that misty puffs are visible in the cool night air. His fingers twitch rhythmically against his knees]. [POINT OF VIEW & GAZE: His eyes are wide, glassy with starlight, fixed on the Milky Way arc. He scans the heavens from left to right with a slow, sweeping ocular movement]. [CAMERA & DEPTH: Low-angle 35mm wide shot. 4K, cinematic, deep focus. Slow dolly push-in (0.2m/s) toward his face]. [TECHNICAL SPEC: Subpixel detail on skin texture, moonlit blue tint (4500K), high dynamic range].",
                "camera_movement": "Slow dolly push-in using a 35mm wide-angle lens at f/11, establishing architectural depth of village rooftops behind.",
                "mood_lighting": "Moonlight from upper-right at 4500K. Ambient starlight fill. Reflections visible in the boy's dilated pupils.",
                "duration_seconds": 6,
                "transition_type": "fade",
                "motion_intensity": "low",
                "key_elements": ["rooftop texture", "starry night", "breathing mist"],
                "character_details": "Raju is in a state of meditative awe. His weight is balanced. His eyes track individual stars. His shoulders rise and fall 2cm with each breath. He sees the infinite cosmos.",
                "continuity_notes": "ESTABLISHES ENVIRONMENT. Raju is stationary. Sets up the gaze for the light's arrival in Scene 2."
            },
            {
                "scene_number": 2,
                "narrative_beat": "आसमान से रहस्यमय रोशनी आती है (Mock Output)",
                "visual_prompt": "[SETTING ANCHOR: Same moonlit village rooftop, exact same houses in background]. [SUBJECT: Raju, same 10yo boy in blue shirt, sitting in same cross-legged position]. [ACTION & MOVEMENT: Picking up from the peaceful gaze, his body suddenly jolts. His spine straightens. His hands grip his knees, knuckles whitening. His mouth falls agape, tongue visible. Sharp, sudden intake of breath]. [POINT OF VIEW & GAZE: His eyes lock onto a descending golden-white orb. He tracks it as it drops from the upper-left sky toward him]. [CAMERA & DEPTH: Medium shot. 50mm lens. Rack focus from the stars to Raju's widening eyes as the light descends]. [TECHNICAL SPEC: Volumetric light rays (6000K) from the orb reflecting off rooftop tiles. Match motion of orbit descent].",
                "camera_movement": "Whip pan following the light's descent, then quick rack focus to Raju's face. 50mm lens f/2.8.",
                "mood_lighting": "Two-tone: Established moonlight (4500K) mixed with dynamic golden-white light burst (6000K) from the descending orb.",
                "duration_seconds": 5,
                "transition_type": "eyeline_match",
                "motion_intensity": "high",
                "key_elements": ["golden orb", "rooftop shadows", "startled expression"],
                "character_details": "Raju's reaction is visceral. Facial muscles tighten. His pupils contract as the light gets closer. He sees the brilliant orb painting trails on his retinas.",
                "continuity_notes": "CAUSAL CHAIN: Startled by the light from Scene 1. Maintains spatial position on rooftop. Prepares for fairy reveal."
            },
            {
                "scene_number": 3,
                "narrative_beat": "रोशनी परी में बदलती है (Mock Output)",
                "visual_prompt": "[SETTING ANCHOR: Same moonlit rooftop, orb now hovering 1 meter from Raju]. [SUBJECT: Raju and the Fairy. Fairy is 15cm tall, translucent wings pulsing]. [ACTION & MOVEMENT: The orb coalesces into a fairy form. Raju slowly, with a trembling right elbow, extends his hand. The movement is jerky, cautious. The Fairy reaches back with a smooth, fluid finger extension]. [POINT OF VIEW & GAZE: Raju looks directly at the fairy's eyes. Fairy maintains a compassionate gaze with a gentle head tilt]. [CAMERA & DEPTH: Close-up with shallow 1.8f DOF. Tracking arc shot rotating 90 degrees]. [TECHNICAL SPEC: Iridescent skin (4800K), subpixel wing flutter, 4K sharp focus on the emerging hands].",
                "camera_movement": "Slow arc shot (3 seconds) rotating around the center point between their heads. Anamorphic lens flare.",
                "mood_lighting": "Subsurface scattering on the fairy's skin. Warm 4800K glow from her wings casting highlights onto Raju's blue shirt.",
                "duration_seconds": 7,
                "transition_type": "motion_match",
                "motion_intensity": "medium",
                "key_elements": ["wing translucency", "trembling hand", "iridescent particles"],
                "character_details": "Raju's fear turns to curiosity. His right hand moves at 0.1m/s. His eyes are wet with wonder. He sees the smallest details of the fairy's starlight dress.",
                "continuity_notes": "CAUSAL CHAIN: Orb from Scene 2 transforms. Hand reaching is a continuation of his curiosity. Leads to the touch."
            },
            {
                "scene_number": 4,
                "narrative_beat": "हाथ मिलने पर जादुई चमक फैलती है (Mock Output)",
                "visual_prompt": "[SETTING ANCHOR: Extreme close-up of center-frame connection point]. [SUBJECT: Raju's tanned finger and Fairy's glowing fingertip]. [ACTION & MOVEMENT: The exactly moment of contact. A shockwave ripple through Raju's skin at the contact point. The Fairy's wings expand to full span]. [POINT OF VIEW & GAZE: Raju's eyes squint from the sudden burst. Fairy's eyes remain open, glowing brighter]. [CAMERA & DEPTH: Macro lens extreme close-up. Focus snap at impact]. [TECHNICAL SPEC: Multi-directional light burst (6500K), 120fps slow motion, subpixel skin texture, HDR bloom].",
                "camera_movement": "Macro steady shot with a tiny micro-vibration 'shake' at the moment of contact. 100mm macro lens.",
                "mood_lighting": "White-out burst. Golden-white omnidirectional blast (6500K) filling the frames, then receding to reveal glowing fingertips.",
                "duration_seconds": 4,
                "transition_type": "match_cut",
                "motion_intensity": "high",
                "key_elements": ["finger contact", "shockwave", "light bloom"],
                "character_details": "Raju feels the energy pulse. His hair lifts slightly from the energy wave. His iris contracts fully. He sees the moment the physical world meets the magical.",
                "continuity_notes": "CLIMAX. The energy burst from the previous scene's reach. Justifies the transport to the sky in Scene 5."
            },
            {
                "scene_number": 5,
                "narrative_beat": "राजू और परी बादलों के ऊपर उड़ रहे हैं (Mock Output)",
                "visual_prompt": "[SETTING ANCHOR: Aerial night sky, 500m above the village rooftops established in Scene 1]. [SUBJECT: Raju and Fairy soaring, holding hands]. [ACTION & MOVEMENT: They soar horizontally. Raju's legs kick slightly as if swimming in air. His left arm is extended like a wing. His shirt ripples violently in the wind]. [POINT OF VIEW & GAZE: Raju looks down at the tiny village below, then up at the moon. He sees the curving horizon]. [CAMERA & DEPTH: Ultra-wide 24mm aerial tracking shot. Depth layers with clouds passing in foreground and village far below]. [TECHNICAL SPEC: Motion blur, moonlight (4500K) on clouds, same starlight pattern from Scene 1].",
                "camera_movement": "Sweeping wide aerial track. 24mm lens at f/8. Perspective shift while maintaining village geography below.",
                "mood_lighting": "Moonlight (4500K) from above. Fairy glow (4800K) lighting Raju's side profile. Dim 3000K sparks from the village far below.",
                "duration_seconds": 8,
                "transition_type": "dissolve",
                "motion_intensity": "medium",
                "key_elements": ["floating clouds", "village miniatures", "wind-swept hair"],
                "character_details": "Raju is elated. His laughter is silent but visible. His eyes are wide, taking in the scale of the world. He sees his house as a tiny dot.",
                "continuity_notes": "RESOLUTION. Final stage of the causal chain. Maintains the nighttime logic and character appearance from the start."
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
