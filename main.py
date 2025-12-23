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
    
    parser.add_argument("--input", "-i", type=str, default="story.txt", 
                       help="Path to the story file (default: story.txt)")
    parser.add_argument("--output", "-o", type=str, default="production_sheet", 
                       help="Base name for output files without extension (default: production_sheet)")
    parser.add_argument("--style", "-s", type=str, default="cinematic",
                       choices=["cinematic", "documentary", "commercial", "artistic", "anime"],
                       help="Visual style preset (default: cinematic)")
    parser.add_argument("--format", "-f", type=str, default="all",
                       choices=["csv", "json", "markdown", "all"],
                       help="Output format (default: all)")
    parser.add_argument("--model", "-m", type=str, default="gemini-2.0-flash-exp",
                       help="Gemini model to use (default: gemini-2.0-flash-exp)")
    parser.add_argument("--target-duration", "-d", type=int, default=None,
                       help="Target video duration in seconds (optional)")
    
    args = parser.parse_args()

    # Print header
    console.print(Panel.fit(
        "[bold cyan]Flow Video Director[/bold cyan]\n"
        "AI-Powered Cinematic Prompt Generator",
        border_style="cyan"
    ))

    # 1. Read the Input Script
    if not os.path.exists(args.input):
        console.print(f"[bold red]✗ Error:[/bold red] File '{args.input}' not found.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        story_text = f.read()

    console.print(f"[bold blue]📖 Story Loaded:[/bold blue] {args.input}")
    console.print(f"[bold blue]🎨 Style:[/bold blue] {args.style.capitalize()}")
    
    if args.target_duration:
        console.print(f"[bold blue]⏱️  Target Duration:[/bold blue] {args.target_duration}s")
    
    console.print("")
    
    # 2. Initialize the Director
    director = VirtualDirector(style=args.style, model_name=args.model)

    # 3. Process the Story
    scenes = director.process_script(story_text, target_duration=args.target_duration)

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
        "model": args.model,
        "source_file": args.input
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
    console.print("[dim]💡 Tip: Use these prompts directly in Google Veo (Flow), Runway, or other AI video generators![/dim]")


if __name__ == "__main__":
    main()

