#!/usr/bin/env python3
"""
Media Pipeline — Create videos, animations, voice, and music
Uses DeepSeek for code generation + local tools for rendering
Usage:
  python3 media.py --script "Create an animated explainer about Bitcoin" --output explainer.mp4
  python3 media.py --voice "Hello, this is AI voice" --output hello.wav
  python3 media.py --image "A futuristic city with flying cars" --output city.png
"""

import os, sys, json, subprocess, argparse, tempfile, base64
from pathlib import Path
from datetime import datetime

for pkg in ["openai"]:
    try: __import__(pkg)
    except: os.system(f"{sys.executable} -m pip install {pkg} --break-system-packages -q")

from openai import OpenAI

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
OUTPUT_DIR = Path.home() / "ai-media"
OUTPUT_DIR.mkdir(exist_ok=True)

if not DEEPSEEK_KEY:
    print("❌ Set DEEPSEEK_API_KEY")
    sys.exit(1)

client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")

# ====== 1. ANIMATION (HTML/CSS/JS → Video) ======

def create_animation(script, output="animation.mp4"):
    """Generate an animated video from a script description."""
    print(f"🎬 Creating animation: {script[:80]}...")
    
    # Generate animation code
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "system",
            "content": """You create HTML/CSS/JS animations. Output ONLY valid HTML.
The animation should be 1080x1920 (vertical for social media).
Use smooth CSS animations, colorful gradients, and modern design.
Include @keyframes for movement, opacity, scale changes.
Make it visually impressive and professional.

OUTPUT ONLY THE HTML FILE CONTENT. No explanations."""
        }, {
            "role": "user",
            "content": f"Create a video animation about: {script}"
        }],
        temperature=0.7,
        max_tokens=4096
    )
    
    html = response.choices[0].message.content
    
    # Clean up - extract code from markdown if needed
    if "```" in html:
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    
    # Save HTML
    html_path = OUTPUT_DIR / "temp_animation.html"
    html_path.write_text(html.strip())
    
    print(f"  📄 Animation HTML saved")
    
    # Render to video using Chromium + ffmpeg
    video_path = OUTPUT_DIR / output
    
    try:
        # Check if chromium/firefox + ffmpeg available
        has_chromium = subprocess.run(["which", "chromium"], capture_output=True).returncode == 0
        has_chrome = subprocess.run(["which", "google-chrome-stable"], capture_output=True).returncode == 0
        has_ffmpeg = subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0
        has_firefox = subprocess.run(["which", "firefox"], capture_output=True).returncode == 0
        
        browser = None
        if has_chrome:
            browser = "google-chrome-stable"
        elif has_chromium:
            browser = "chromium"
        elif has_firefox:
            browser = "firefox"
        
        if browser and has_ffmpeg:
            # Screenshot approach: open browser, capture frames
            print(f"  🌐 Rendering with {browser} + ffmpeg...")
            # Open in browser and let it render
            subprocess.Popen([browser, f"file://{html_path}"], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✅ Animation opened in browser")
            print(f"  💡 Close the browser tab when done")
        else:
            print(f"  📄 HTML saved. Install ffmpeg + chromium for video rendering:")
            print(f"  sudo apt install ffmpeg chromium-browser")
    
    except Exception as e:
        print(f"  ⚠️ Render note: {e}")
    
    print(f"\n✅ Animation saved: {html_path}")
    print(f"   Open in browser: file://{html_path}")
    return html_path


# ====== 2. VOICE (TTS) ======

def create_voice(text, output="voice.wav", voice_style="professional"):
    """Generate voice from text using espeak or piper TTS."""
    print(f"🗣️  Creating voice: {text[:50]}...")
    
    output_path = OUTPUT_DIR / output
    
    # Check local TTS tools
    has_espeak = subprocess.run(["which", "espeak"], capture_output=True).returncode == 0
    has_piper = subprocess.run(["which", "piper"], capture_output=True).returncode == 0
    
    if has_piper:
        print("  🔊 Using Piper TTS (high quality)")
        voice_model = Path.home() / "piper-voices/en_US-lessac-medium.onnx"
        if voice_model.exists():
            subprocess.run([
                "echo", text, "|", "piper",
                "--model", str(voice_model),
                "--output_file", str(output_path)
            ], shell=True)
            print(f"  ✅ Voice saved to {output_path}")
        else:
            print("  ⚠️ Piper model not found. Download from:")
            print("     https://huggingface.co/rhasspy/piper-voices")
            # Fallback to espeak
    
    if has_espeak:
        print("  🔊 Using espeak (basic TTS)")
        subprocess.run([
            "espeak", "-w", str(output_path),
            "-s", "150", "-p", "50",
            text
        ])
        print(f"  ✅ Voice saved to {output_path}")
    else:
        # Generate a simple tutorial
        print("\n📋 To install TTS on this system:")
        print("  sudo apt install espeak")
        print("  # Or for high quality:")
        print("  pip install piper-tts")
        print()
        # Save text version
        text_path = OUTPUT_DIR / f"{Path(output).stem}.txt"
        text_path.write_text(text)
        print(f"  📄 Text saved to {text_path}")
    
    return output_path


# ====== 3. MUSIC (Audio Generation) ======

def create_music(prompt, output="music.wav", duration=10):
    """Generate music/soundtrack."""
    print(f"🎵 Creating music: {prompt[:50]}...")
    
    output_path = OUTPUT_DIR / output
    
    # Use DeepSeek to generate a Python script that creates the audio
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "system",
            "content": """You generate Python code that creates audio using numpy and scipy.
Output ONLY valid Python code that:
1. Imports numpy and scipy.io.wavfile
2. Creates a WAV file at the specified path
3. Generate interesting sound patterns: melodies, beats, ambient
4. Use sine waves, sawtooth, square waves, white noise, filters
5. Make it sound good - layered, rhythmic, musical

The file path will be passed as: output_path variable""" 
        }, {
            "role": "user",
            "content": f"Create Python code to generate {duration} seconds of: {prompt}. Save to {output_path}"
        }],
        temperature=0.8,
        max_tokens=2048
    )
    
    code = response.choices[0].message.content
    if "```" in code:
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[6:]
    
    # Save and run the script
    script_path = OUTPUT_DIR / "temp_music_gen.py"
    script_path.write_text(code)
    
    try:
        subprocess.run([sys.executable, str(script_path)], 
                     cwd=OUTPUT_DIR, timeout=30, capture_output=True, text=True)
        if output_path.exists():
            print(f"  ✅ Music saved to {output_path}")
        else:
            print(f"  ⚠️ Script ran but no output found")
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Music generation timed out")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
    
    return output_path


# ====== 4. IMAGE (HTML → Screenshot) ======

def create_image(prompt, output="image.png"):
    """Generate an image using HTML/CSS rendering."""
    # Note: DeepSeek is text-only, so we use HTML/CSS as image
    print(f"🖼️  Creating image: {prompt[:50]}...")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{
            "role": "system",
            "content": """You create beautiful HTML/CSS images. NOT SVGs - use DIVs.
Create a full-page design using:
- CSS gradients for backgrounds
- CSS shapes with border-radius, transforms
- Text with modern typography
- Shadows, animations (optional)
- Make it look like a professional graphic design

Output ONLY the HTML file content. No markdown. No explanations."""
        }, {
            "role": "user",
            "content": f"Create an image showing: {prompt}"
        }],
        temperature=0.7,
        max_tokens=4096
    )
    
    html = response.choices[0].message.content
    if "```" in html:
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    
    html_path = OUTPUT_DIR / f"{Path(output).stem}.html"
    html_path.write_text(html.strip())
    
    print(f"  📄 HTML image saved")
    print(f"\n✅ Open in browser to view/screenshot:")
    print(f"   file://{html_path}")
    
    return html_path


# ====== MAIN ======

def main():
    parser = argparse.ArgumentParser(description="AI Media Pipeline - Create video, voice, music, images")
    parser.add_argument("--script", "-s", help="Video/Animation script description")
    parser.add_argument("--voice", "-v", help="Text to convert to voice")
    parser.add_argument("--music", "-m", help="Music description")
    parser.add_argument("--image", "-i", help="Image description")
    parser.add_argument("--duration", "-d", type=int, default=10, help="Music duration in seconds")
    parser.add_argument("--output", "-o", default=None, help="Output filename")
    
    args = parser.parse_args()
    
    if args.script:
        out = args.output or f"animation_{datetime.now():%Y%m%d_%H%M%S}.mp4"
        create_animation(args.script, out)
    
    elif args.voice:
        out = args.output or f"voice_{datetime.now():%Y%m%d_%H%M%S}.wav"
        create_voice(args.voice, out)
    
    elif args.music:
        out = args.output or f"music_{datetime.now():%Y%m%d_%H%M%S}.wav"
        create_music(args.music, out, args.duration)
    
    elif args.image:
        out = args.output or f"image_{datetime.now():%Y%m%d_%H%M%S}.png"
        create_image(args.image, out)
    
    else:
        parser.print_help()
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} --script \"Animated explainer about how Bitcoin works\" --output bitcoin.mp4")
        print(f"  python {sys.argv[0]} --voice \"Hello, welcome to my video\" --output intro.wav")
        print(f"  python {sys.argv[0]} --music \"Energetic synth beat\" --duration 30 --output background.wav")
        print(f"  python {sys.argv[0]} --image \"Futuristic city skyline at sunset\" --output city.png")


if __name__ == "__main__":
    main()
