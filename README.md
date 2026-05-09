# AI Pipeline 🧠

> One command to access all AI capabilities — chat, code, media, and local models.
> Designed for **M2 Ultra** but works anywhere with DeepSeek API.

```
ai chat "What's new in crypto?"
ai code "Create a FastAPI trading API"
ai media --script "Bitcoin explainer video"
ai model status
```

---

## Features

### 💬 `ai chat` — AI Chat (like Claude)
- DeepSeek API as primary engine (cheap: ~$0.28/M tokens)
- Automatic fallback to local Ollama if API fails
- Streaming output, file reading, conversation history
- Interactive session mode with save/load/reset

### 💻 `ai code` — Coding Agent (like Cursor)
- Generate full projects from natural language descriptions
- Auto-extracts files from AI output and saves them to disk
- Auto-tests by running `main.py` after generation
- Debug existing files with `--debug`
- Projects stored in `~/ai-code-projects/`

### 🎬 `ai media` — Media Creation
- **Animation**: Generates HTML/CSS/JS animations for explainers
- **Voice**: Text-to-speech via Piper TTS (high quality) or espeak
- **Music**: Generates Python scripts that create WAV audio
- **Image**: Renders CSS-based graphic designs (no GenAI image model needed)

### 🖥️ `ai model` — Local Model Management
- Install/manage Ollama, MLX, Diffusers, TTS
- Status check for MPS availability (M2 Ultra GPU)
- Disk space reporting

---

## Installation

### Quick Install (one-liner)

```bash
git clone https://github.com/yahyasaqban-lab/ai-pipeline.git
cd ai-pipeline
source setup.sh   # adds the `ai` command to your shell
```

### Manual Setup

```bash
# 1. Set your DeepSeek API key (or skip for local-only mode)
export DEEPSEEK_API_KEY="sk-your-key-here"

# 2. (Optional) Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export DEEPSEEK_API_KEY="sk-your-key-here"' >> ~/.zshrc
echo 'source /path/to/ai-pipeline/setup.sh' >> ~/.zshrc

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Alternative: Use `ai` directly

```bash
python3 ai.py chat "Hello"
python3 ai.py code "Build a trading bot"
python3 ai.py media --script "Explain Bitcoin"
python3 ai.py model status
```

---

## 🦙 Using a Local Model (Ollama) Instead of DeepSeek

No API key? No problem. Run entirely offline with Ollama.

### 1. Install Ollama

```bash
# macOS (your M2)
curl -fsSL https://ollama.com/install.sh | sh

# Or via Homebrew
brew install ollama
```

### 2. Pull a model

```bash
ollama pull llama3.2          # Lightweight (3B, fast)
ollama pull llama3.1          # Balanced (8B)
ollama pull qwen2.5:32b       # Powerful (32B, needs good RAM)
```

### 3. Run Ollama server

```bash
ollama serve &
```

### 4. Use ai-pipeline without DeepSeek key

Simply **don't set** `DEEPSEEK_API_KEY`. The `ai chat` module auto-detects:

```bash
unset DEEPSEEK_API_KEY
ai chat "Hello, how are you?"
# → Output: 🖥️ Local model (free, private)
# → Uses Ollama's API at http://localhost:11434/v1
```

You can also set a custom Ollama endpoint or model by editing `chat/chat.py`:

```python
# In __init__:
self.client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
self.model = "llama3.2"   # Change this to any model you pulled
```

### Local vs API Comparison

| | DeepSeek API | Ollama (local) |
|---|---|---|
| **Cost** | ~$0.28/M tokens | Free |
| **Speed** | Fast (cloud GPU) | Depends on model size |
| **Privacy** | Data sent to API | 100% local |
| **Requires** | API key + internet | Ollama installed + model downloaded |
| **M2 Ultra** | Overkill but works | Leverages 192GB RAM for big models |

---

## Usage

### Chat

```bash
# One-shot
ai chat "What's the latest on Bitcoin?"

# With file analysis
ai chat --file data.txt "Summarize this"

# Streaming response
ai chat --stream "Tell me a story"

# Interactive session
ai chat --interactive

# Load previous session
ai chat --session 20250508_143022

# List saved sessions
ai chat --list
```

### Coding

```bash
# Create a project
ai code "Create a FastAPI app with 3 endpoints"

# With custom project name
ai code --name my-trading-bot "Python trading bot with Binance API"

# Debug a file
ai code --debug myapp.py

# List existing projects
ai code --list
```

### Media

```bash
# Animation
ai media --script "Animated explainer about how Bitcoin works" --output bitcoin.mp4

# Voice
ai media --voice "Hello, welcome to my video" --output intro.wav

# Music (generates a Python script that creates WAV)
ai media --music "Energetic synth beat" --duration 30 --output background.wav

# Image (HTML/CSS design)
ai media --image "Futuristic city skyline at sunset" --output city.png
```

### Model Management (run on M2)

```bash
# Check status
ai model status

# Install tools
ai model install-ollama
ai model install-mlx
ai model install-all
```

---

## Project Structure

```
ai-pipeline/
├── ai.py              # Master launcher — entry point
├── setup.sh           # Shell setup (adds `ai` command + auto-completion)
├── requirements.txt   # Python dependencies
├── .gitignore
├── README.md
├── chat/
│   └── chat.py        # AI chat module (DeepSeek + Ollama)
├── coding/
│   └── coding.py      # Coding agent (project generation)
├── media/
│   └── media.py       # Media creation (animation, voice, music, image)
├── model/
│   └── setup.py       # Local model installer & status checker
└── config/            # (optional) Config files
```

---

## Requirements

- **Python 3.10+**
- **DeepSeek API key** (set `DEEPSEEK_API_KEY` env var)
- **Optional for media:**
  - `ffmpeg` — for video rendering
  - `chromium` / `firefox` — for animation rendering
  - `espeak` — basic TTS
  - `piper-tts` — high quality TTS
- **Optional for local models:**
  - [Ollama](https://ollama.com) — local LLMs
  - [MLX](https://github.com/ml-explore/mlx) — Apple Silicon ML
  - macOS with Apple Silicon (M-series) for best local performance

---

## Design Philosophy

- **API-first**: DeepSeek provides cheap, fast inference (no GPU needed)
- **Fallback chain**: API → local model → graceful failure
- **Minimal dependencies**: Only `openai` and `requests` required
- **Apple Silicon optimized**: MPS acceleration, MLX support
- **Privacy**: No telemetry, no data collection, open source

---

## License

MIT
