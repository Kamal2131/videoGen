import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from director import VirtualDirector
from exporters import SceneExporter, calculate_statistics
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables from .env file
load_dotenv()

console = Console()


def display_statistics(scenes):
    """Display statistics about the generated scenes."""
    stats = calculate_statistics(scenes)
    
    if not stats:
        return
    
    # Create statistics panel
    stats_text = f"""
[cyan]Total Scenes:[/cyan] {stats['total_scenes']}
[cyan]Total Duration:[/cyan] {stats['total_duration_seconds']:.1f}s ({stats['total_duration_minutes']:.2f} minutes)
[cyan]Average Scene Duration:[/cyan] {stats['average_scene_duration']:.1f}s

[cyan]Motion Distribution:[/cyan]
"""
    
    for motion, count in stats.get('motion_distribution', {}).items():
        stats_text += f"  • {motion.capitalize()}: {count} scenes\n"
    
    console.print(Panel(stats_text.strip(), title="📊 Production Statistics", border_style="green"))


def display_scenes_table(scenes):
    """Display scenes in a formatted table."""
    table = Table(title="🎬 Master Production Sheet")
    table.add_column("Scene", justify="right", style="cyan", no_wrap=True)
    table.add_column("Beat", style="yellow", max_width=25)
    table.add_column("Visual Prompt", style="magenta", max_width=50)
    table.add_column("Duration", justify="center", style="green")
    table.add_column("Motion", justify="center", style="blue")

    for scene in scenes:
        table.add_row(
            str(scene.get("scene_number", "?")),
            scene.get("narrative_beat", "")[:25] + "..." if len(scene.get("narrative_beat", "")) > 25 else scene.get("narrative_beat", ""),
            scene.get("visual_prompt", "")[:50] + "..." if len(scene.get("visual_prompt", "")) > 50 else scene.get("visual_prompt", ""),
            f"{scene.get('duration_seconds', 5)}s",
            scene.get("motion_intensity", "?")[:3].upper()
        )
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="🎬 Flow Video Director - Convert Stories to Production-Ready Video Prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input story.txt
  python main.py -i story.txt --style cinematic --format all
  python main.py -i story.txt --style anime --target-duration 60
  python main.py -i story.txt --model gemini-1.5-flash --output custom_output
        """
    )
    
    parser.add_argument("--input", "-i", dest="input_file", required=False,
                       help="Path to input story text file")
    parser.add_argument("--load-file", "-l", dest="load_file",
                       help="Path to existing JSON production sheet (skips LLM generation)")
    parser.add_argument("--output", "-o", type=str, default="production_sheet", 
                       help="Base name for output files without extension (default: production_sheet)")
    parser.add_argument("--style", "-s", type=str, default="cinematic",
                       choices=["cinematic", "documentary", "commercial", "artistic", "anime"],
                       help="Visual style preset (default: cinematic)")
    parser.add_argument("--provider", "-p", type=str, default=os.getenv("DEFAULT_PROVIDER", "gemini"),
                       choices=["gemini", "groq"],
                       help="AI provider (default: from .env or gemini)")
    parser.add_argument("--format", "-f", type=str, default="all",
                       choices=["csv", "json", "markdown", "all"],
                       help="Output format (default: all)")
    parser.add_argument("--model", "-m", type=str, default=None,
                       help="Model to use (default: gemini-2.0-flash-exp for Gemini, llama-3.3-70b-versatile for Groq)")
    parser.add_argument("--target-duration", "-d", type=int, default=None,
                       help="Target video duration in seconds (optional)")
    
    # Video generation arguments
    parser.add_argument("--generate-videos", action="store_true",
                       help="Generate actual videos using Google Veo 2 API (requires GCP setup)")
    parser.add_argument("--video-output-dir", type=str, default="generated_videos",
                       help="Directory to save generated videos (default: generated_videos)")
    parser.add_argument("--parallel-videos", type=int, default=2,
                       help="Number of videos to generate in parallel (default: 2)")
    
    args = parser.parse_args()

    # Print header
    console.print(Panel.fit(
        "[bold cyan]Flow Video Director[/bold cyan]\n"
        "AI-Powered Cinematic Prompt Generator",
        border_style="cyan"
    ))

    
    # Initialize variables
    scenes = []
    model_name = args.model or "unknown"
    
    # PATH A: Load existing scenes (Manual/No-LLM Mode)
    if args.load_file:
        if not os.path.exists(args.load_file):
            console.print(f"[red]Error: File not found: {args.load_file}[/red]")
            return
            
        console.print(f"[bold cyan]📂 Loading scenes from: {args.load_file}[/bold cyan]")
        try:
            import json
            with open(args.load_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both raw list and envelope format
                if isinstance(data, dict) and "scenes" in data:
                    scenes = data["scenes"]
                    model_name = data.get("metadata", {}).get("model", "manual-load")
                elif isinstance(data, list):
                    scenes = data
                    model_name = "manual-list"
                else:
                    console.print("[red]Error: Invalid JSON format. Expected list of scenes or object with 'scenes' key.[/red]")
                    return
            console.print(f"[green]✓ Successfully loaded {len(scenes)} scenes[/green]")
            
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
            return

    # PATH B: Generate using AI Director (LLM Mode)
    elif args.input_file:
        if not os.path.exists(args.input_file):
            console.print(f"[bold red]✗ Error:[/bold red] File '{args.input_file}' not found.")
            return

        with open(args.input_file, "r", encoding="utf-8") as f:
            story_text = f.read()

        console.print(f"[bold blue]📖 Story Loaded:[/bold blue] {args.input_file}")
        console.print(f"[bold blue]🎨 Style:[/bold blue] {args.style.capitalize()}")
        
        # Determine model default if not provided
        if not args.model:
            if args.provider == 'groq':
                model_name = 'llama-3.3-70b-versatile'
            else:
                model_name = 'gemini-2.0-flash-exp'
        else:
            model_name = args.model
            
        director = VirtualDirector(style=args.style, model_name=model_name, provider=args.provider)
        
        console.print(f"[bold cyan]🎬 Director analyzing script...[/bold cyan]")
        scenes = director.process_script(story_text, target_duration=args.target_duration)
        
    else:
        console.print("[red]Error: You must provide either --input (to generate) or --load-file (to load existing)[/red]")
        parser.print_help()
        return

    if not scenes:
        console.print("[red]✗ No scenes generated.[/red]")
        return

    console.print("")
    
    # 4. Display Results
    display_scenes_table(scenes)
    console.print("")
    display_statistics(scenes)
    console.print("")

    # 5. Export to selected format(s)
    metadata = {
        "style": args.style,
        "provider": args.provider,
        "model": model_name,
        "source_file": args.input_file or args.load_file
    }
    
    if args.target_duration:
        metadata["target_duration"] = args.target_duration
    
    exporter = SceneExporter(scenes, metadata)
    
    console.print("[cyan]📁 Exporting production sheets...[/cyan]")
    
    exported_files = []
    
    if args.format == "all":
        files = exporter.export_all(args.output)
        exported_files = list(files.values())
    else:
        if args.format == "csv":
            filename = f"{args.output}.csv"
            exporter.to_csv(filename)
            exported_files.append(filename)
        elif args.format == "json":
            filename = f"{args.output}.json"
            exporter.to_json(filename)
            exported_files.append(filename)
        elif args.format == "markdown":
            filename = f"{args.output}.md"
            exporter.to_markdown(filename)
            exported_files.append(filename)
    
    console.print("[bold green]✓ Success! Production sheets exported:[/bold green]")
    for file in exported_files:
        console.print(f"  • {file}")
    
    console.print("")
    
    # 6. Optional: Generate actual videos using Veo 2 API
    if args.generate_videos:
        try:
            from video_generator import VeoVideoGenerator
            
            console.print("[bold cyan]🎥 Starting Video Generation...[/bold cyan]")
            console.print("")
            
            generator = VeoVideoGenerator(
                project_id=os.getenv("GCP_PROJECT_ID"),
                location=os.getenv("GCP_LOCATION", "us-central1")
            )
            
            # Generate videos for all scenes
            video_files = generator.generate_batch(
                scenes,
                output_dir=args.video_output_dir,
                parallel_count=args.parallel_videos
            )
            
            console.print("")
            if video_files:
                console.print("[bold green]✓ Videos generated successfully![/bold green]")
                console.print(f"[green]Output directory: {args.video_output_dir}[/green]")
            else:
                console.print("[yellow]⚠ No videos were generated. Check errors above.[/yellow]")
        
        except ImportError:
            console.print("[red]Error: Video generation requires google-cloud-aiplatform[/red]")
            console.print("[yellow]Install with: pip install google-cloud-aiplatform[/yellow]")
        except Exception as e:
            console.print(f"[red]Video generation failed: {e}[/red]")
    else:
        console.print("[dim]💡 Tip: Use these prompts in Google Veo (Flow), Runway, or add --generate-videos to auto-generate![/dim]")


if __name__ == "__main__":
    main()

