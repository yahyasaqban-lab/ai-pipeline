#!/usr/bin/env python3
"""
Model Pipeline — Run AI models locally on M2 Ultra
- Text generation (Ollama, MLX)
- Image generation (Stable Diffusion via diffusers)
- Voice (XTTS-v2, Piper)
- Vision (LLaVA, Qwen-VL)

Designed for M2 Ultra 192GB. Run these scripts ON THE M2.
"""
import subprocess, sys, os
from pathlib import Path

CONFIG_DIR = Path.home() / ".ai-models"
CONFIG_DIR.mkdir(exist_ok=True)

def install_ollama():
    """Install Ollama for easy local LLM management."""
    print("🦙 Installing Ollama...")
    subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"], shell=True)
    print("✅ Ollama installed")
    print("   Pull a model: ollama pull llama3")
    print("   Run: ollama run llama3")

def install_mlx():
    """Install MLX for Apple Silicon training/inference."""
    print("🍎 Installing MLX...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mlx", "mlx-lm"])
    print("✅ MLX installed")
    print("   Use: mlx_lm.generate --model Qwen/Qwen2.5-72B-Instruct")

def install_stable_diffusion():
    """Install Stable Diffusion for image generation."""
    print("🎨 Installing Stable Diffusion...")
    subprocess.run([sys.executable, "-m", "pip", "install", "diffusers", "transformers", "accelerate", "torch"])
    print("✅ Stable Diffusion deps installed")
    print("   Use: from diffusers import StableDiffusion3Pipeline")

def install_tts():
    """Install TTS models."""
    print("🗣️  Installing TTS...")
    subprocess.run([sys.executable, "-m", "pip", "install", "TTS"])
    print("✅ TTS installed")
    print("   Use: tts --text 'Hello' --model_name tts_models/en/ljspeech/tacotron2-DDC")

def status():
    """Show what's installed."""
    checks = {
        "Ollama": subprocess.run(["which", "ollama"], capture_output=True).returncode == 0,
        "MLX": subprocess.run([sys.executable, "-c", "import mlx"], capture_output=True).returncode == 0,
        "PyTorch": subprocess.run([sys.executable, "-c", "import torch; print(torch.backends.mps.is_available())"], capture_output=True).returncode == 0,
        "Diffusers": subprocess.run([sys.executable, "-c", "import diffusers"], capture_output=True).returncode == 0,
        "TTS": subprocess.run([sys.executable, "-c", "import TTS"], capture_output=True).returncode == 0,
        "ffmpeg": subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0,
    }
    
    print("\n📊 Model Pipeline Status")
    print("=" * 30)
    for name, ok in checks.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    print()
    
    if checks["PyTorch"]:
        import torch
        print(f"  MPS Available: {torch.backends.mps.is_available()}")
        if torch.backends.mps.is_available():
            print(f"  GPU: M2 Ultra")
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    print(f"  Free disk: {free // (2**30)} GB")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "install-ollama": install_ollama()
    elif cmd == "install-mlx": install_mlx()
    elif cmd == "install-sd": install_stable_diffusion()
    elif cmd == "install-tts": install_tts()
    elif cmd == "install-all":
        install_ollama()
        install_mlx()
        install_stable_diffusion()
        install_tts()
    else:
        status()
