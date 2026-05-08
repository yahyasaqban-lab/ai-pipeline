#!/usr/bin/env python3
"""
AI Pipeline — Master Launcher
One command to access all AI capabilities:
  ai chat "What's new in crypto?"
  ai code "Create a trading bot"
  ai media --script "Bitcoin explainer video"
  ai model status
"""

import sys, argparse
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent

def main():
    parser = argparse.ArgumentParser(description="AI Pipeline — Your personal AI platform")
    sub = parser.add_subparsers(dest="command")
    
    # Chat
    chat_p = sub.add_parser("chat", help="Chat with AI (like Claude)")
    chat_p.add_argument("prompt", nargs="*")
    chat_p.add_argument("--file", "-f")
    chat_p.add_argument("--interactive", "-i", action="store_true")
    chat_p.add_argument("--stream", "-s", action="store_true")
    chat_p.add_argument("--list", action="store_true")
    
    # Code
    code_p = sub.add_parser("code", help="Coding agent (like Cursor)")
    code_p.add_argument("task", nargs="*")
    code_p.add_argument("--debug", "-d")
    code_p.add_argument("--name", "-n")
    code_p.add_argument("--list", "-l", action="store_true")
    
    # Media
    media_p = sub.add_parser("media", help="Create animations, voice, music, images")
    media_p.add_argument("--script", "-s")
    media_p.add_argument("--voice", "-v")
    media_p.add_argument("--music", "-m")
    media_p.add_argument("--image", "-i")
    media_p.add_argument("--duration", type=int, default=10)
    media_p.add_argument("--output", "-o")
    
    # Model
    model_p = sub.add_parser("model", help="Manage local AI models (M2 Ultra)")
    model_p.add_argument("action", nargs="?", default="status",
                       choices=["status", "install-ollama", "install-mlx", "install-all"])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print()
        print("  🧠 chat   — Chat with AI (like Claude)")
        print("  💻 code   — Coding agent (like Cursor)")
        print("  🎬 media  — Create videos, voice, music, images")
        print("  🖥️  model  — Manage local AI models on M2")
        print()
        print("  Set DEEPSEEK_API_KEY in your environment")
        return
    
    if args.command == "chat":
        from chat.chat import AIChat, main as chat_main
        chat_main()
    
    elif args.command == "code":
        from coding.coding import CodingAgent, main as code_main
        code_main()
    
    elif args.command == "media":
        from media.media import main as media_main
        media_main()
    
    elif args.command == "model":
        from model.setup import status as model_status
        os.system(f"{sys.executable} {PIPELINE_DIR}/model/setup.py {' '.join(sys.argv[2:])}")


if __name__ == "__main__":
    main()
