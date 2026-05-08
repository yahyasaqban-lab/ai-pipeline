#!/usr/bin/env python3
"""
AI Chat Pipeline — Replaces Claude for daily use
- Primary: DeepSeek API (cheap, fast)
- Fallback: Local Ollama model (free, private)
- Supports: streaming, file reading, conversation memory
Usage:
  python3 chat.py "What's the latest on Bitcoin?"
  python3 chat.py --file data.txt "Summarize this"
  python3 chat.py --stream "Tell me a story"
"""

import os, sys, json, re, argparse
from pathlib import Path
from datetime import datetime

# Auto-install
for pkg in ["openai", "requests"]:
    try:
        __import__(pkg)
    except:
        os.system(f"{sys.executable} -m pip install {pkg} --break-system-packages -q")

from openai import OpenAI

# Config
HISTORY_DIR = Path.home() / ".ai-chat-history"
HISTORY_DIR.mkdir(exist_ok=True)
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

SYSTEM_PROMPT = """You are a helpful AI assistant with broad knowledge.
You give clear, accurate, thoughtful answers.
You can analyze files, code, and complex topics.
Think step by step for difficult questions."""

class AIChat:
    def __init__(self):
        self.provider = "deepseek"
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize DeepSeek
        if DEEPSEEK_KEY:
            self.client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")
            self.model = "deepseek-chat"
            print(f"🧠 DeepSeek API (cheap, $0.28/M tokens)")
        else:
            # Fallback: try local Ollama
            try:
                self.client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
                self.model = "llama3"
                print(f"🖥️  Local model (free, private)")
            except:
                print("❌ No API key. Set DEEPSEEK_API_KEY or run Ollama locally")
                sys.exit(1)
    
    def ask(self, prompt, stream=False, file_path=None):
        """Send a message and get a response."""
        
        # Read file if provided
        if file_path:
            p = Path(file_path)
            if p.exists():
                content = p.read_text(encoding='utf-8', errors='ignore')[:15000]
                prompt = f"Here's a file ({p.name}):\n\n{content}\n\n{prompt}"
        
        self.messages.append({"role": "user", "content": prompt})
        
        if stream:
            return self._stream_response()
        else:
            return self._normal_response()
    
    def _normal_response(self):
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=4096,
                timeout=60
            )
            reply = r.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            self._save()
            return reply
        except Exception as e:
            # Try fallback
            if "401" in str(e) or "402" in str(e) or "insufficient" in str(e).lower():
                return self._try_ollama_fallback(prompt)
            return f"Error: {e}"
    
    def _stream_response(self):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
                timeout=60
            )
            full = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    print(text, end='', flush=True)
                    full += text
            print()
            self.messages.append({"role": "assistant", "content": full})
            self._save()
            return full
        except Exception as e:
            return f"Error: {e}"
    
    def _try_ollama_fallback(self, prompt):
        print("\n⚠️  DeepSeek failed. Trying local Ollama...")
        try:
            c = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
            r = c.chat.completions.create(model="llama3", messages=self.messages, max_tokens=4096)
            reply = r.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            self._save()
            return f"[Local Model]\n{reply}"
        except:
            return "❌ Both DeepSeek and local model failed."
    
    def _save(self):
        path = HISTORY_DIR / f"{self.session_id}.jsonl"
        with open(path, 'w') as f:
            for msg in self.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    
    def load_session(self, session_id):
        path = HISTORY_DIR / f"{session_id}.jsonl"
        if path.exists():
            self.messages = [json.loads(l) for l in path.read_text().strip().split('\n')]
            return True
        return False
    
    def list_sessions(self):
        sessions = sorted(HISTORY_DIR.glob("*.jsonl"))
        for s in sessions[-10:]:
            created = datetime.fromtimestamp(s.stat().st_mtime).strftime("%m/%d %H:%M")
            size = s.stat().st_size
            msg_count = len(s.read_text().strip().split('\n')) - 1
            print(f"  {s.stem}  ({created}, {msg_count} msgs, {size} bytes)")
        return sessions


def main():
    parser = argparse.ArgumentParser(description="AI Chat — Claude replacement")
    parser.add_argument("prompt", nargs="*", help="Your question or message")
    parser.add_argument("--file", "-f", help="Read a file and ask about it")
    parser.add_argument("--stream", "-s", action="store_true", help="Stream response")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive chat mode")
    parser.add_argument("--session", help="Load a previous session")
    parser.add_argument("--list", action="store_true", help="List saved sessions")
    
    args = parser.parse_args()
    
    chat = AIChat()
    
    if args.list:
        chat.list_sessions()
        return
    
    if args.session:
        if chat.load_session(args.session):
            print(f"📋 Loaded session: {args.session}")
        else:
            print(f"❌ Session not found: {args.session}")
            return
    
    if args.interactive:
        print(f"💬 AI Chat (type 'quit' to exit, 'save' to save, 'clear' to reset)")
        print(f"   Session: {chat.session_id}")
        print()
        while True:
            try:
                user = input("\nYou: ").strip()
                if user.lower() in ("quit", "exit", "q"): break
                if user.lower() == "clear": chat.messages = chat.messages[:1]; print("🧹 Reset"); continue
                if user.lower() == "save": print(f"💾 Saved: {chat.session_id}"); continue
                if user.lower().startswith("/load "):
                    chat.load_session(user[6:].strip())
                    print(f"📋 Loaded session: {user[6:].strip()}")
                    continue
                if user:
                    print("\nAI: ", end='', flush=True)
                    chat.ask(user, stream=True)
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye")
                break
    elif args.prompt:
        prompt = " ".join(args.prompt)
        reply = chat.ask(prompt, stream=args.stream, file_path=args.file)
        if not args.stream:
            print(reply)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
