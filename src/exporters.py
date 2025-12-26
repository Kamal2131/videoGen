"""
Flow Video Generation - Export Module

Handles exporting scene data to various formats:
- Enhanced CSV with all fields
- JSON with metadata
- Markdown production sheet
"""

import json
import csv
from datetime import datetime
from typing import List, Dict


class SceneExporter:
    """Handles exporting scenes to multiple formats."""
    
    def __init__(self, scenes: List[Dict], metadata: Dict = None):
        """
        Initialize exporter with scene data.
        
        Args:
            scenes: List of scene dictionaries
            metadata: Optional metadata about the generation
        """
        self.scenes = scenes
        self.metadata = metadata or {}
        
    def to_csv(self, output_path: str):
        """Export scenes to enhanced CSV format."""
        if not self.scenes:
            return
        
        # Get all unique keys from all scenes
        fieldnames = set()
        for scene in self.scenes:
            fieldnames.update(scene.keys())
        
        # Ensure consistent ordering with important fields first
        ordered_fields = ['scene_number', 'narrative_beat', 'visual_prompt', 
                         'camera_movement', 'mood_lighting', 'duration_seconds',
                         'transition_type', 'motion_intensity', 'key_elements',
                         'audio_suggestion']
        
        # Add any extra fields that might exist
        fieldnames = [f for f in ordered_fields if f in fieldnames] + \
                    [f for f in sorted(fieldnames) if f not in ordered_fields]
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for scene in self.scenes:
                # Convert lists to strings for CSV
                row = {}
                for key, value in scene.items():
                    if isinstance(value, list):
                        row[key] = ', '.join(str(v) for v in value)
                    else:
                        row[key] = value
                writer.writerow(row)
    
    def to_json(self, output_path: str):
        """Export scenes to JSON format with metadata."""
        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_scenes": len(self.scenes),
                "total_duration_seconds": sum(s.get('duration_seconds', 5) for s in self.scenes),
                **self.metadata
            },
            "scenes": self.scenes
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def to_markdown(self, output_path: str):
        """Export scenes to human-readable markdown production sheet."""
        lines = []
        
        # Header
        lines.append("# Master Production Sheet")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Scenes:** {len(self.scenes)}")
        
        total_duration = sum(s.get('duration_seconds', 5) for s in self.scenes)
        lines.append(f"**Estimated Duration:** {total_duration} seconds ({total_duration/60:.1f} minutes)")
        
        if self.metadata:
            lines.append("")
            lines.append("## Generation Settings")
            for key, value in self.metadata.items():
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Scenes
        for scene in self.scenes:
            scene_num = scene.get('scene_number', '?')
            lines.append(f"## Scene {scene_num}")
            
            if 'narrative_beat' in scene:
                lines.append(f"**Beat:** {scene['narrative_beat']}")
                lines.append("")
            
            if 'visual_prompt' in scene:
                lines.append("### Visual Prompt")
                lines.append(f"> {scene['visual_prompt']}")
                lines.append("")
            
            # Technical details in a table
            lines.append("| Aspect | Details |")
            lines.append("|--------|---------|")
            
            if 'camera_movement' in scene:
                lines.append(f"| 🎥 Camera | {scene['camera_movement']} |")
            
            if 'mood_lighting' in scene:
                lines.append(f"| 💡 Lighting | {scene['mood_lighting']} |")
            
            if 'duration_seconds' in scene:
                lines.append(f"| ⏱️ Duration | {scene['duration_seconds']} seconds |")
            
            if 'transition_type' in scene:
                lines.append(f"| 🔀 Transition | {scene['transition_type']} |")
            
            if 'motion_intensity' in scene:
                lines.append(f"| 🎬 Motion | {scene['motion_intensity']} |")
            
            if 'audio_suggestion' in scene:
                lines.append(f"| 🔊 Audio | {scene['audio_suggestion']} |")
            
            lines.append("")
            
            if 'key_elements' in scene and scene['key_elements']:
                lines.append("**Key Elements:**")
                if isinstance(scene['key_elements'], list):
                    for element in scene['key_elements']:
                        lines.append(f"- {element}")
                else:
                    lines.append(f"- {scene['key_elements']}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def export_all(self, base_path: str):
        """
        Export to all formats with automatic naming.
        
        Args:
            base_path: Base filename without extension (e.g., 'output/production_sheet')
        """
        self.to_csv(f"{base_path}.csv")
        self.to_json(f"{base_path}.json")
        self.to_markdown(f"{base_path}.md")
        
        return {
            'csv': f"{base_path}.csv",
            'json': f"{base_path}.json",
            'markdown': f"{base_path}.md"
        }


def calculate_statistics(scenes: List[Dict]) -> Dict:
    """Calculate useful statistics about the scenes."""
    if not scenes:
        return {}
    
    total_duration = sum(s.get('duration_seconds', 5) for s in scenes)
    
    motion_counts = {}
    transition_counts = {}
    
    for scene in scenes:
        motion = scene.get('motion_intensity', 'unknown')
        motion_counts[motion] = motion_counts.get(motion, 0) + 1
        
        transition = scene.get('transition_type', 'unknown')
        transition_counts[transition] = transition_counts.get(transition, 0) + 1
    
    return {
        'total_scenes': len(scenes),
        'total_duration_seconds': total_duration,
        'total_duration_minutes': total_duration / 60,
        'average_scene_duration': total_duration / len(scenes),
        'motion_distribution': motion_counts,
        'transition_distribution': transition_counts
    }
