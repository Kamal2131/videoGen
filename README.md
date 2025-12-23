# 🎬 Flow Video Director

Transform stories and scripts into production-ready AI video prompts optimized for **Google Veo (Flow)**, **Runway Gen-3**, and other advanced AI video generation platforms.

## ✨ Features

- **Dual AI Provider Support**: Use Google Gemini OR Groq (FREE!)
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

Create a `.env` file with your API key(s):

```env
# Option 1: Use Groq (RECOMMENDED - 100% FREE!)
GROQ_API_KEY=your_groq_key_here

# Option 2: Use Google Gemini
GOOGLE_API_KEY=your_gemini_key_here

# You can have both and switch between them!
```

**Get FREE Groq API Key:** Visit [console.groq.com](https://console.groq.com) - No credit card required!

### Basic Usage

```bash
# Use Groq (FREE, ultra-fast)
python main.py -i story.txt --provider groq

# Use Gemini
python main.py -i story.txt --provider gemini

# Generate with specific style
python main.py -i story.txt --provider groq --style anime

# Target specific duration
python main.py -i story.txt --provider groq --target-duration 60

# Export specific format
python main.py -i story.txt --provider groq --format json
```

## 🤖 AI Provider Options

### Groq (Recommended - FREE!)

**Why Groq:**
- ✅ **100% FREE** - Generous free tier, no billing required
- ✅ **Ultra Fast** - Fastest LLM inference available
- ✅ **High Quality** - Excellent for creative prompts

**Available Models:**
- `llama-3.3-70b-versatile` (Default - Latest & Best)
- `llama3-70b-8192` (Llama 3.0 70B)
- `llama3-8b-8192` (Faster, smaller)
- `mixtral-8x7b-32768` (Large context window)
- `gemma2-9b-it` (Google's Gemma)

**Usage:**
```bash
python main.py -i story.txt --provider groq
python main.py -i story.txt --provider groq --model llama3-70b-8192
```

### Google Gemini

**Available Models:**
- `gemini-2.0-flash-exp` (Default - Latest experimental)
- `gemini-1.5-flash` (Stable fallback)
- `gemini-1.5-pro` (Most capable)

**Usage:**
```bash
python main.py -i story.txt --provider gemini
python main.py -i story.txt --provider gemini --model gemini-1.5-pro
```

**Note:** Gemini has free tier limits. If you hit quota, Groq is a great free alternative!

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
--provider, -p      AI provider: groq or gemini (default: gemini)
--style, -s         Style preset (cinematic/documentary/commercial/artistic/anime)
--format, -f        Output format (csv/json/markdown/all)
--model, -m         Model to use (auto-selected based on provider)
--target-duration   Target video duration in seconds
```

## 🌟 Example Workflows

### 1. Quick Start with Groq (FREE)
```bash
python main.py -i story.txt --provider groq
```

### 2. Generate Anime-Style Video with Groq
```bash
python main.py -i story.txt --provider groq --style anime --format all
```

### 3. Precise Duration Control
```bash
python main.py -i story.txt --provider groq --target-duration 45 --style cinematic
```

### 4. Use Gemini with Specific Model
```bash
python main.py -i story.txt --provider gemini --model gemini-1.5-pro
```

### 5. Fast Iterations with Smaller Model
```bash
python main.py -i story.txt --provider groq --model llama3-8b-8192
```

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
- **Provider Flexibility**: Switch between Groq and Gemini seamlessly

## 💡 Tips for Best Results

- **Use Groq for free unlimited generations** - No billing required!
- Be descriptive in your story for richer visual prompts
- Use the `--target-duration` flag to control video length
- Try different styles to find the best aesthetic for your project
- Review the markdown output for the most readable production sheet
- Use character names consistently for better consistency tracking
- If Gemini quota is exceeded, switch to `--provider groq`

## 🆚 Provider Comparison

| Feature | Groq | Gemini |
|---------|------|--------|
| **Cost** | 🟢 FREE (Generous limits) | 🟡 Free tier limited |
| **Speed** | 🟢 Ultra Fast | 🟡 Fast |
| **Quality** | 🟢 Excellent | 🟢 Excellent |
| **Setup** | 🟢 Easy, no billing | 🟡 May need billing |

## 📚 Project Structure

```
videoGen/
├── main.py              # Main application with CLI
├── director.py          # Virtual Director with dual provider support
├── prompts.py           # System instructions and style presets
├── exporters.py         # Multi-format export handlers
├── story.txt            # Your input story
├── .env                 # API keys configuration
└── production_sheet.*   # Generated outputs
```

## 🔑 API Key Setup

### Groq (Recommended)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (FREE, no credit card)
3. Create API key
4. Add to `.env`: `GROQ_API_KEY=your_key`

### Google Gemini
1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Get API key
3. Add to `.env`: `GOOGLE_API_KEY=your_key`

---

**Made with ❤️ for filmmakers, storytellers, and AI video enthusiasts**

**Quick Support:**
- 💬 Issues? Check your API key in `.env`
- 🔄 Hit Gemini quota? Switch to `--provider groq`
- 📖 Questions? Review examples above or run `python main.py --help`

