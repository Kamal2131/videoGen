import os
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# New Imports from src package
from src.director import VirtualDirector
from src.exporters import SceneExporter, calculate_statistics
from src.generators.factory import get_video_generator
from src.config import Config

console = Console()

def display_statistics(scenes):
    """Display statistics about the generated scenes."""
    stats = calculate_statistics(scenes)
    if not stats: return
    
    stats_text = f"""
[cyan]Total Scenes:[/cyan] {stats['total_scenes']}
[cyan]Total Duration:[/cyan] {stats['total_duration_seconds']:.1f}s
[cyan]Average Scene Duration:[/cyan] {stats['average_scene_duration']:.1f}s
"""
    console.print(Panel(stats_text.strip(), title="📊 Production Statistics", border_style="green"))

def display_scenes_table(scenes):
    """Display scenes in a formatted table."""
    table = Table(title="🎬 Master Production Sheet")
    table.add_column("Scene", justify="right", style="cyan", no_wrap=True)
    table.add_column("Beat", style="yellow", max_width=40)
    table.add_column("Visual Prompt", style="magenta", max_width=60)
    
    for scene in scenes:
        table.add_row(
            str(scene.get("scene_number", "?")),
            scene.get("narrative_beat", "")[:40],
            scene.get("visual_prompt", "")[:60] + "..."
        )
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="🎬 Flow Video Director (Multi-Provider)")
    
    parser.add_argument("--input", "-i", dest="input_file", help="Path to input story file")
    parser.add_argument("--style", "-s", default="cinematic", help="Visual style")
    
    # Provider Selection
    parser.add_argument("--provider", "-p", default=Config.DEFAULT_PROVIDER, 
                        choices=["gemini", "openai", "groq"],
                        help="AI Provider for Script Analysis (Director)")
    
    parser.add_argument("--video-provider", "-vp", default="gemini",
                        choices=["gemini", "openai"],
                        help="AI Provider for Video Generation")

    # Video Generation
    parser.add_argument("--generate-videos", action="store_true", help="Generate actual videos")
    parser.add_argument("--video-output-dir", default=Config.Video_OUTPUT_DIR, help="Output dir for videos")

    args = parser.parse_args()

    console.print(Panel.fit("[bold cyan]Flow Video Director 2.0[/bold cyan]\nMulti-Provider Engine", border_style="cyan"))

    # 1. LOAD SCRIPT
    if not args.input_file:
        console.print("[red]Error: Please provide --input <file>[/red]")
        return
        
    with open(args.input_file, "r", encoding="utf-8") as f:
        story_text = f.read()

    # 2. RUN DIRECTOR (Script -> Scenes)
    console.print(f"[bold blue]Step 1: The Director ({args.provider.upper()})[/bold blue]")
    director = VirtualDirector(provider=args.provider, style=args.style)
    scenes = director.process_script(story_text)

    if not scenes:
        console.print("[red]No scenes generated.[/red]")
        return

    display_scenes_table(scenes)
    display_statistics(scenes)
    
    # 3. EXPORT DATA
    exporter = SceneExporter(scenes, {"style": args.style, "provider": args.provider})
    files = exporter.export_all("production_sheet")
    console.print(f"[green]✓ Exported {len(files)} files (CSV, JSON, MD)[/green]")

    # 4. GENERATE VIDEOS (Scenes -> MP4)
    if args.generate_videos:
        console.print(f"\n[bold blue]Step 2: Video Generation ({args.video_provider.upper()})[/bold blue]")
        
        generator = get_video_generator(args.video_provider)
        
        # Check if actually initialized
        # In a real app we might check generator.is_ready() 
        
        generator.generate_batch(scenes, args.video_output_dir)

if __name__ == "__main__":
    main()
