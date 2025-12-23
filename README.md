# 🎬 Flow Video Director

Transform stories and scripts into production-ready AI video prompts optimized for **Google Veo (Flow)**, **Runway Gen-3**, and other advanced AI video generation platforms.

## ✨ Features

- **Flow-Optimized Prompts**: Structured prompts following best practices for Google Veo (Flow)
- **Character Consistency**: Maintains identical character descriptions across all scenes
- **Multiple Style Presets**: Cinematic, Documentary, Commercial, Artistic, and Anime styles
- **Enhanced Scene Metadata**: Duration, transitions, motion intensity, and audio suggestions
- **Multiple Export Formats**: CSV, JSON, and beautifully formatted Markdown production sheets
- **Statistics Dashboard**: Comprehensive scene analysis and duration tracking

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your Google Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

### Basic Usage

```bash
# Simple generation with cinematic style (default)
python main.py --input story.txt

# Generate with specific style
python main.py -i story.txt --style anime

# Target specific duration
python main.py -i story.txt --target-duration 60

# Export specific format
python main.py -i story.txt --format json

# Custom model
python main.py -i story.txt --model gemini-1.5-flash
```

## 🎨 Style Presets

- **`cinematic`**: Feature film style with dramatic camera work and anamorphic aesthetics
- **`documentary`**: Realistic, handheld camera work with natural lighting
- **`commercial`**: Polished, high-production value with vibrant colors
- **`artistic`**: Creative freedom with experimental techniques
- **`anime`**: Animation-style with vibrant colors and exaggerated expressions

## 📊 Output Formats

### CSV Format
Perfect for spreadsheet viewing and editing. Includes all scene details in tabular format.

### JSON Format
Structured data with complete metadata, ideal for programmatic use and integrations.

### Markdown Format
Beautiful, human-readable production sheet with formatted tables and organized sections.

## 🎯 The Flow Methodology

Our prompts follow the optimal structure for Flow video generation:

1. **SUBJECT**: Clear character/object descriptions with consistency
2. **ACTION**: Precise movement and activity descriptions
3. **SETTING**: Detailed environment and atmosphere
4. **CAMERA**: Professional camera angles, movements, and lens specifications
5. **LIGHTING**: Specific lighting setups with technical details

## 📖 Command-Line Options

```
--input, -i         Path to story file (default: story.txt)
--output, -o        Base name for output files (default: production_sheet)
--style, -s         Style preset (cinematic/documentary/commercial/artistic/anime)
--format, -f        Output format (csv/json/markdown/all)
--model, -m         Gemini model to use (default: gemini-2.0-flash-exp)
--target-duration   Target video duration in seconds
```

## 🌟 Example Workflow

1. Write your story in `story.txt` (any language supported)
2. Run: `python main.py -i story.txt --style cinematic --format all`
3. Review generated scenes in the terminal
4. Use exported prompts in Google Veo or Runway
5. Generate your cinematic video!

## 📝 Sample Output

The system generates detailed prompts like:

```
Wide establishing shot: A young Indian boy, approximately 10 years old, 
wearing a faded blue cotton shirt and dark shorts, sits cross-legged on 
a terracotta rooftop. The night sky above is filled with countless 
twinkling stars. Ancient village houses visible in background. 35mm lens, 
deep focus, 4K resolution, cinematic composition, dreamy atmosphere.
```

Complete with camera movements, lighting specs, duration, and transitions!

## 🔧 Advanced Features

- **Character Consistency**: Automatically maintains identical character descriptions
- **Duration Control**: Smart scene splitting based on target duration
- **Transition Planning**: Suggests appropriate transitions between scenes
- **Motion Analysis**: Categorizes scene motion intensity
- **Audio Suggestions**: Recommends background sounds and music

## 💡 Tips for Best Results

- Be descriptive in your story for richer visual prompts
- Use the `--target-duration` flag to control video length
- Try different styles to find the best aesthetic for your project
- Review the markdown output for the most readable production sheet
- Use character names consistently for better consistency tracking

## 📚 Project Structure

```
videoGen/
├── main.py          # Main application
├── director.py      # Virtual Director with Flow optimization
├── prompts.py       # System instructions and style presets
├── exporters.py     # Multi-format export handlers
├── story.txt        # Your input story
└── production_sheet.*  # Generated outputs
```

## 🎓 Learn More

For more about Google Veo (Flow) and optimal prompt engineering, visit the official documentation.

---

**Made with ❤️ for filmmakers, storytellers, and AI video enthusiasts**

