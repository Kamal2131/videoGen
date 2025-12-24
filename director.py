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
    console.print("[bold yellow]Note:[/bold yellow] 'google-generativeai' library not found.")

# Try to import Groq
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    console.print("[bold yellow]Note:[/bold yellow] 'groq' library not found.")


class VirtualDirector:
    """
    Enhanced Virtual Director with Flow-specific optimizations.
    
    Features:
    - Flow-optimized prompt engineering
    - Character consistency tracking
    - Multiple style presets
    - Enhanced scene structure
    """
    
    def __init__(self, api_key=None, style="cinematic", model_name='gemini-2.0-flash-exp', provider='gemini'):
        """
        Initialize the Virtual Director.
        
        Args:
            api_key: API key (defaults to GOOGLE_API_KEY or GROQ_API_KEY env var)
            style: Style preset ('cinematic', 'documentary', 'commercial', 'artistic', 'anime')
            model_name: Model to use (gemini-2.0-flash-exp, llama-3.1-70b-versatile, etc.)
            provider: AI provider ('gemini' or 'groq')
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.style = style
        self.style_defaults = get_style_defaults(style)
        self.character_profiles = {}
        self.model = None
        self.model_name = model_name
        
        # Initialize based on provider
        if self.provider == 'groq':
            self._init_groq(model_name, style)
        else:  # default to gemini
            self._init_gemini(model_name, style)
    
    def _init_gemini(self, model_name, style):
        """Initialize Gemini provider."""
        if HAS_GENAI and self.api_key:
            genai.configure(api_key=self.api_key)
            system_instruction = get_system_instruction(style)
            
            try:
                self.model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_instruction
                )
                console.print(f"[green]✓ Virtual Director ready[/green] (Provider: Gemini, Model: {model_name}, Style: {style})")
            except Exception as e:
                console.print(f"[yellow]Could not initialize {model_name}: {e}[/yellow]")
                console.print("[yellow]Trying fallback model: gemini-1.5-flash[/yellow]")
                try:
                    self.model = genai.GenerativeModel(
                        'gemini-1.5-flash',
                        system_instruction=system_instruction
                    )
                    self.model_name = 'gemini-1.5-flash'
                    console.print(f"[green]✓ Virtual Director ready[/green] (Provider: Gemini, Model: gemini-1.5-flash, Style: {style})")
                except Exception as e2:
                    console.print(f"[red]Failed to initialize Gemini: {e2}[/red]")
                    self.model = None
        else:
            if not HAS_GENAI:
                console.print("[yellow]Gemini library not installed. Running in MOCK MODE.[/yellow]")
            else:
                console.print("[bold red]Warning:[/bold red] No GOOGLE_API_KEY found. Running in [bold yellow]MOCK MODE[/bold yellow].")
    
    def _init_groq(self, model_name, style):
        """Initialize Groq provider."""
        if HAS_GROQ and self.api_key:
            try:
                self.model = Groq(api_key=self.api_key)
                console.print(f"[green]✓ Virtual Director ready[/green] (Provider: Groq, Model: {model_name}, Style: {style})")
            except Exception as e:
                console.print(f"[red]Failed to initialize Groq: {e}[/red]")
                self.model = None
        else:
            if not HAS_GROQ:
                console.print("[yellow]Groq library not installed. Install with: pip install groq[/yellow]")
            else:
                console.print("[bold red]Warning:[/bold red] No GROQ_API_KEY found. Running in [bold yellow]MOCK MODE[/bold yellow].")

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
        """Generate with Gemini API."""
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
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
        Enhanced mock response with all new fields demonstrating scene interlinking and depth.
        """
        return [
            {
                "scene_number": 1,
                "narrative_beat": "लड़का छत पर तारों को देख रहा है (Mock Output)",
                "visual_prompt": "Wide establishing shot: A young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, sits cross-legged on a terracotta rooftop of an old village house. His body is still, hands resting gently on his knees, head tilted upward at a 45-degree angle, eyes wide with wonder scanning the vast starry sky above, mouth slightly open in quiet amazement, breathing slowly and peacefully. The night sky is deep indigo filled with thousands of twinkling stars forming the Milky Way arc. Behind him, ancient village houses with slanted tile roofs create layered silhouettes against the horizon, a few dim oil lamps glowing softly in distant windows. Moonlight from upper right casts a cool blue-white glow (4500K) across his face and the rooftop, creating subtle shadows. 35mm wide-angle lens, deep focus f/11, 4K resolution, cinematic composition, film grain, dreamy atmosphere, peaceful and serene mood.",
                "camera_movement": "Slow ascending crane shot starting low at rooftop level, rising 2 meters over 5 seconds to establish scene, 35mm lens maintaining deep focus on both boy and expansive sky",
                "mood_lighting": "Primary moonlight source from upper right at 4500K creating soft blue-white illumination, distant warm village lamp glow at 3000K in background providing ambient fill, cool starlight highlights creating ethereal atmosphere, high contrast shadows defining rooftop edges",
                "duration_seconds": 6,
                "transition_type": "fade",
                "motion_intensity": "low",
                "key_elements": ["boy on rooftop", "starry sky with Milky Way", "layered village silhouettes", "moonlight atmosphere"],
                "audio_suggestion": "Gentle night crickets chirping rhythmically, distant village sounds (dog barking faintly, wind chimes), soft ambient music with sparse piano notes building wonder",
                "character_details": "Raju sits perfectly still in meditation-like posture, his weight balanced evenly, spine straight but relaxed. His eyes slowly travel across the sky left to right, pupils dilated to capture the starlight, occasionally blinking slowly. His chest rises and falls with calm breaths, visible in the cool night air. He sees the infinite cosmos above, the Milky Way's arc painting the heavens, individual stars twinkling like distant lanterns.",
                "continuity_notes": "ESTABLISHES: Nighttime village rooftop setting with moonlit atmosphere and starry sky - this lighting and environment will continue. Sets peaceful mood that will be disrupted by mysterious light arrival. Camera ends in elevated position ready to follow descending light in next scene."
            },
            {
                "scene_number": 2,
                "narrative_beat": "आसमान से रहस्यमय रोशनी आती है (Mock Output)",
                "visual_prompt": "Medium shot transitioning to close-up: The same young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, still seated cross-legged on the same terracotta rooftop under the same moonlit starry sky. Suddenly, his relaxed expression shifts - eyes widen dramatically, pupils contracting, eyebrows rising, mouth opening in surprise. His body tenses, shoulders pulling back slightly. He tracks something with his eyes, head tilting back further, now at 60-degree angle looking almost straight up. A brilliant white-gold orb of light (6500K) descends rapidly from the star-filled sky above, leaving a shimmering ethereal trail of glowing particles. The orb grows from a pinpoint to soccer-ball size, its intense glow reflecting in the boy's wide eyes, casting new highlights across his face and illuminating the rooftop tiles around him with dancing light patterns. Same village houses visible in background, now partially illuminated by the descending light. The established cool blue moonlight (4500K) mixes with the warm-white orb glow creating dynamic two-tone lighting. 50mm portrait lens, shallow depth of field f/2.8, volumetric light rays, high dynamic range HDR, hyper-realistic texture, 4K cinematic, anamorphic lens flare from bright orb.",
                "camera_movement": "Camera continues from elevated position, quickly tilts up following the boy's eye-line to capture descending light, then whip pans back down and pushes in rapidly to medium close-up of boy's face, 50mm lens with focus rack from background to boy's eyes",
                "mood_lighting": "Layered lighting combining established moonlight (4500K from upper right) with NEW dramatic descending light orb (intense 6500K white-gold), creating rim lighting on boy's face, strong highlights in his eyes, dual shadows on rooftop, maintaining background village lamp warmth (3000K) for depth",
                "duration_seconds": 5,
                "transition_type": "eyeline_match",
                "motion_intensity": "high",
                "key_elements": ["descending light orb with trail", "boy's startled reaction", "dynamic lighting shift", "volumetric light rays", "same rooftop environment"],
                "audio_suggestion": "Building on previous ambient crickets, add ethereal whooshing sound growing louder as light descends, rising tension music with strings, boy's sharp intake of breath, magical shimmer sound effect",
                "character_details": "Raju's entire body reacts to the phenomenon - muscles tense, hands grip his knees tightly, fingers curling. His head jerks upward tracking the light's descent, eyes locked on the orb, unblinking from shock and awe. His breathing quickens, visible as faster chest movements, heartbeat racing. He sees the brilliant orb descending directly toward him, its light so bright it creates afterimages, its trail painting streaks across his vision. Fear and wonder battle in his expression - wanting to retreat but unable to look away.",
                "continuity_notes": "CONTINUES: Same rooftop location, maintains moonlit environment, boy in same seated position. CHANGES: Introduces magical light element that adds new light source while preserving established atmosphere. LEADS TO: Light's descent creates anticipation for its arrival/transformation. Camera position shifting closer prepares for intimate fairy reveal next."
            },
            {
                "scene_number": 3,
                "narrative_beat": "रोशनी परी में बदलती है (Mock Output)",
                "visual_prompt": "Slow motion close-up transitioning to medium shot: The bright white-gold orb (6500K) now hovers at arm's length from the young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, still on the same moonlit terracotta rooftop with starry sky above and village silhouettes behind. The orb pulses with energy, its form becoming fluid and reshaping over 2 seconds. Ethereal particles swirl and coalesce, the intense white light softening to a warm iridescent glow (4800K) with subtle rainbow refractions. The light transforms into the delicate form of a tiny fairy - 15cm tall, with translucent dragonfly-like wings that shimmer with opalescent blues and purples, wearing a flowing dress made of starlight, long flowing hair that seems to emit soft light, large kind eyes, and a gentle smile. She extends her small right hand forward gracefully, fingers spread elegantly, palm up in offering gesture. The boy, expression shifting from fear to wonder, slowly begins raising his trembling right hand, palm open, fingers slightly curved and shaking, eyes fixated on the fairy's glowing form, mouth slightly agape showing amazement, breathing visible in the cool night air as misty puffs. The established cool moonlight (4500K) from upper right remains, now mixing with the fairy's internal warm glow creating magical soft shadows on the rooftop. Village houses still visible in background, maintaining environmental consistency. Anamorphic 2.39:1 aspect ratio, shallow depth of field f/2.2 with beautiful bokeh on background lights, magical particles floating in air catching highlights, 8K ultra detail, cinematic color grade with teal shadows and golden highlights, film grain, dreamlike atmosphere.",
                "camera_movement": "Camera picks up from previous close position, executes graceful slow circular arc tracking shot rotating 120 degrees around the transformation in 4 seconds, then gentle push-in toward fairy and boy's hands as they prepare to touch, anamorphic lens creating horizontal flares from fairy's glow",
                "mood_lighting": "Complex three-source lighting: primary established moonlight (4500K upper right) maintaining scene, NEW fairy's internal warm iridescent glow (4800K with rainbow refraction) as magical fill light illuminating both characters' faces from center, distant village lamps (3000K) still providing background depth. Soft magical particles catching highlights throughout, creating ethereal atmosphere while maintaining nighttime rooftop consistency.",
                "duration_seconds": 7,
                "transition_type": "motion_match",
                "motion_intensity": "medium",
                "key_elements": ["light-to-fairy transformation with particle effects", "fairy's extended hand", "boy's trembling hand rising", "maintained rooftop environment", "magical atmospheric glow", "background bokeh"],
                "audio_suggestion": "Continuing ambient crickets at lower volume, magical transformation sound with crystalline chimes and soft whoosh, ethereal female vocal harmony emerging, boy's breath quickening with wonder, gentle heartbeat-like bass undertone building emotional connection",
                "character_details": "Raju's fear melts into pure wonder - his tense muscles gradually relax, though his hand still trembles with nervousness and excitement. His right hand lifts slowly from his knee, elbow bending, forearm rising, palm rotating upward to mirror the fairy's gesture. His fingers quiver slightly, spreading apart then curving gently. His eyes, still wide, now filled with tears of amazement that catch the fairy's light, creating tiny rainbow refractions. His breathing is shallow and quick, chest rising and falling rapidly. He sees the fairy's delicate features, her kind smile, her outstretched hand inviting connection - the most magical sight he's ever witnessed. His head leans forward slightly, drawn to the wonder before him.",
                "continuity_notes": "CONTINUES: Exact same rooftop location and moonlit starry night established in scene 1, environmental consistency maintained throughout. DEVELOPS: Light phenomenon from scene 2 completes transformation to character form, adding new light source that complements rather than replaces established lighting. LEADS TO: Hands approaching creates anticipation for magical touch moment in next scene. Camera's circular motion and push-in creates intimacy and focus on the imminent connection. Lighting setup prepared for magical interaction glow."
            },
            {
                "scene_number": 4,
                "narrative_beat": "हाथ मिलने पर जादुई चमक फैलती है (Mock Output)",  
                "visual_prompt": "Extreme close-up of hands: The young Indian boy's right hand (small, slight build, sun-tanned skin) and the tiny fairy's delicate glowing hand (15cm tall fairy, translucent luminescent skin) meet fingertip to fingertip at the exact center of frame. As contact occurs, a brilliant explosion of golden-white magical energy (6000K) radiates outward in expanding concentric waves of light and glittering particles, creating a flash that illuminates everything. The same moonlit (4500K) rooftop environment visible in soft focus behind, same starry sky, village silhouettes maintained. Camera positioned intimately close, capturing the exact moment of connection in ultra-sharp detail - individual fingerprints, skin texture, the fairy's translucent hand structure, particles of light dancing between them. Macro lens perspective, extremely shallow depth of field f/1.4, magical light rays bursting omnidirectionally, volumetric god rays, lens flare from energy burst, 8K hyper-detail, HDR color grading, slow motion capture at 120fps, cinematic anamorphic aspect ratio.",
                "camera_movement": "Camera holds steady push-in from previous shot, reaching extreme close-up exactly as hands touch, micro-vibration from magical energy impact, then sudden rapid pull-back/zoom-out combination creating vertigo effect to show expanding magical energy wave",
                "mood_lighting": "Dramatic lighting surge: established moonlight (4500K) and fairy glow (4800K) still present but overwhelmed momentarily by intense magical contact energy burst (6000K golden-white), creating omnidirectional lighting filling all shadows, rim lighting on both characters, particles catching highlights, then settling back to combined moonlight + enhanced fairy glow illuminating transformed environment",
                "duration_seconds": 4,
                "transition_type": "match_cut",
                "motion_intensity": "high",
                "key_elements": ["fingertip contact point", "energy burst explosion", "magical particles radiating", "maintained rooftop setting", "slow motion impact"],
                "audio_suggestion": "Building on previous musical theme, massive magical impact sound - crystalline chime explosion with deep resonant bass note, energy wave whoosh expanding, triumphant orchestral swell, crickets momentarily silent from magical force then returning, ethereal choir voices",
                "character_details": "Raju's trembling hand makes contact - the moment his fingertip touches the fairy's hand, an electric tingle shoots through his entire body. His eyes squeeze shut reflexively from the bright flash, face turning slightly away but hand remaining connected, experiencing pure magical energy coursing through him. His whole body illuminated by the burst, hair slightly lifted by the energy wave, clothes rippling. The tiny fairy maintains her gentle smile, eyes glowing with warm light, her wings spreading wide reflexively, whole form becoming more radiant.",
                "continuity_notes": "CONTINUES: Still on established rooftop (consistent location throughout), same moonlit night atmosphere, same characters. CLIMAXES: The anticipated touch moment delivers magical pay-off. TRANSITIONS: Energy burst creates perfect motivation for scene change - magical transport about to occur. Lighting surge justifies shift to next environment while maintaining source consistency (moon+fairy glow will carry into flight scene)."
            },
            {
                "scene_number": 5,
                "narrative_beat": "राजू और परी बादलों के ऊपर उड़ रहे हैं (Mock Output)",
                "visual_prompt": "Wide aerial shot: The young Indian boy, approximately 10 years old, wearing a faded blue cotton shirt and dark shorts, and the tiny glowing fairy (15cm tall with iridescent translucent wings) are now floating 500 meters above the same village, soaring gracefully through the night sky among wisping clouds. They hold hands - Raju's larger hand gently clasping the fairy's tiny glowing hand. His body is suspended horizontally in flight position, his free left arm extended outward for balance, legs bent naturally, hair and clothes rippling in the wind, face showing pure joy and exhilaration with mouth open in delighted laughter, eyes wide scanning the incredible view below. The fairy's wings beat rapidly creating soft light pulse, her dress flowing, guiding their flight path upward and forward. Below them, the entire village is laid out like a miniature model - the same terracotta rooftops (recognizable as where they were), winding dirt paths, temple spires, scattered oil lamp lights creating warm dots of 3000K light, agricultural fields forming geometric patterns, all bathed in the same moonlight (4500K) from above that established the scene. The starry sky surrounds them on all sides, Milky Way arc overhead, thin wispy clouds at their altitude catching moonlight creating silver-white ethereal textures. Continuing fairy's warm glow (4800K) illuminates both characters from their joined hands. Ultra-wide 24mm lens, deep focus f/8 capturing vast scale, 4K cinematic resolution, anamorphic 2.39:1, dramatic depth with multiple distance layers, color graded with cool blues and warm accent lights, film grain, magical atmosphere blending wonder and beauty.",
                "camera_movement": "Camera executes sweeping crane shot ascending and pulling back simultaneously revealing the flight, then transitions to smooth aerial tracking shot flying alongside them at same speed and altitude, 24mm wide lens maintaining environmental scope, gentle floating motion",
                "mood_lighting": "Consistent nighttime lighting: primary moonlight (4500K) from above illuminating clouds and village below maintaining established night atmosphere, fairy's warm iridescent glow (4800K) lighting both characters' faces from their joined hands, village oil lamps below (3000K) creating depth and reference to origin, starlight providing ambient fill, all sources harmonized into magical nighttime flight scene",
                "duration_seconds": 8,
                "transition_type": "dissolve",
                "motion_intensity": "medium",
                "key_elements": ["boy and fairy flying in night sky", "aerial view of village far below (origin location)", "moonlit clouds", "starry sky surrounding", "joined hands glowing", "wind-swept movement"],
                "audio_suggestion": "Wind rushing past creating whoosh sound, continuing magical orchestral theme now triumphant and soaring, boy's delighted laughter, fairy's wings creating soft rhythmic flutter sound, distant village sounds from far below, ethereal choir building to emotional peak",
                "character_details": "Raju experiences pure unbridled joy - no more fear, only wonder and excitement. His body relaxes into the flight, trusting the fairy's magic. His head turns left and right taking in every detail - looking down at the tiny village below (his home now so small!), looking up at the infinite stars above (now so close!), looking at the fairy with gratitude and amazement. His free hand reaches out feeling the cool night wind between his fingers. His laughter is genuine, breath visible in the cold high-altitude air. He sees the world transformed - perspectives shifted, the impossible made real, magic proven true.",
                "continuity_notes": "CONTINUES & ELEVATES: Literally elevates from established rooftop location (now visible far below maintaining spatial geography), same moonlit starry night (lighting consistency maintained, just perspective changed), same characters with consistent appearance. RESOLVES: Completes the story arc from earthbound wonder to magical flight transcendence. Environmental consistency maintained through recognizable village layout, same lighting sources (moon + fairy glow), same nighttime atmosphere - just viewed from above now. Scene could continue or conclude here with fade."
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
