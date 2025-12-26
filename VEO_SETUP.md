# Google Veo 2 Setup Guide

## Prerequisites

1. **Google Cloud Platform Account**
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one
   - Enable billing (required for Veo 2 API)

2. **Enable Vertex AI API**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Install Google Cloud SDK** (gcloud CLI)
   - Download from: https://cloud.google.com/sdk/docs/install
   - Or use: `pip install google-cloud-sdk`

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-cloud-aiplatform` - Vertex AI SDK
- `google-auth` - GCP authentication
- All other existing dependencies

### 2. Authenticate with Google Cloud

**Option A: User Account (Recommended for local development)**
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

**Option B: Service Account (For production/automation)**
1. Create a service account in GCP Console
2. Download the JSON key file
3. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   ```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your GCP details:
```bash
# Your existing keys
GOOGLE_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# NEW - Add these for video generation
GCP_PROJECT_ID=your-gcp-project-id  # From GCP Console
GCP_LOCATION=us-central1            # or us-east4
```

### 4. Verify Setup

Test authentication:
```bash
gcloud auth list
gcloud config get-value project
```

Test video generator:
```bash
python video_generator.py
```

## Usage

### Generate Prompts Only (No Videos)
```bash
python main.py --input story.txt
```

### Generate Prompts + Videos
```bash
python main.py --input story.txt --generate-videos
```

### Advanced Options
```bash
python main.py --input story.txt \
    --generate-videos \
    --parallel-videos 4 \
    --video-output-dir my_videos \
    --style cinematic
```

## CLI Arguments for Video Generation

| Argument | Description | Default |
|----------|-------------|---------|
| `--generate-videos` | Enable video generation via Veo 2 | False |
| `--video-output-dir` | Directory to save videos | `generated_videos` |
| `--parallel-videos` | Concurrent video generations | 2 |

## Cost Estimation

**Veo 2 Pricing** (approximate):
- ~$0.10-0.30 per second of generated video
- 5-second scene: ~$0.50-1.50
- 10-scene video (50 seconds): ~$5-15

**Cost Control Tips**:
1. Start with 1-2 scenes for testing
2. Set up billing alerts in GCP Console
3. Use `--parallel-videos 1` to slow down batch processing
4. Monitor costs at: https://console.cloud.google.com/billing

## Regions

Veo 2 is available in:
- `us-central1` (Iowa)
- `us-east4` (Virginia)

Set your region in `.env`:
```bash
GCP_LOCATION=us-central1
```

## Troubleshooting

### "No GCP_PROJECT_ID found"
- Make sure `.env` file exists and contains `GCP_PROJECT_ID`
- Load dotenv: Check that `python-dotenv` is installed

### "Failed to initialize Vertex AI"
- Run: `gcloud auth application-default login`
- Verify project: `gcloud config get-value project`
- Enable API: `gcloud services enable aiplatform.googleapis.com`

### "Permission denied" errors
- Check IAM roles: Vertex AI User, AI Platform User
- Verify billing is enabled

### Import errors
```bash
# Reinstall dependencies
pip install --upgrade google-cloud-aiplatform
```

## Next Steps

After setup:
1. Test with a short story (1-2 scenes)
2. Monitor generation time (2-5 min per scene)
3. Check video quality and consistency
4. Scale up to full stories

## Support Regions & Models

**Veo Models Available**:
- `veo-2.0-generate-001` - Veo 2 (latest, highest quality)
- `veo-001` - Veo 1 (fallback)

**Parameters**:
- Duration: 5-8 seconds per scene
- Resolution: 720p (Veo 2), 1080p (Veo 3 when available)
- Aspect ratios: 16:9, 9:16, 1:1, 2.39:1
