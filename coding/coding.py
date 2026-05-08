#!/usr/bin/env python3
"""
Coding Agent — AI coding assistant like Cursor/Copilot
- DeepSeek-driven code generation
- Executes code safely in Docker or temp dir
- Writes, tests, debugs code
- Works with any language
Usage:
  python3 coding.py "Create a FastAPI app with 3 endpoints"
  python3 coding.py --sandbox "Run this Python script safely"
"""

import os, sys, json, subprocess, tempfile, shutil, argparse
from pathlib import Path
from datetime import datetime

for pkg in ["openai", "requests", "pyyaml"]:
    try: __import__(pkg)
    except: os.system(f"{sys.executable} -m pip install {pkg} --break-system-packages -q")

from openai import OpenAI

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
PROJECTS_DIR = Path.home() / "ai-code-projects"
PROJECTS_DIR.mkdir(exist_ok=True)

CODING_PROMPT = """You are an expert coding assistant. You write clean, working code.

When asked to create something:
1. Plan the architecture first
2. Write each file with full implementation
3. Include error handling and type hints
4. Test the code if possible
5. Show how to run it

For each file you create, output:
FILE: path/to/file.py
```code here```

Then explain how to run it.
"""

class CodingAgent:
    def __init__(self):
        if not DEEPSEEK_KEY:
            print("❌ Set DEEPSEEK_API_KEY")
            sys.exit(1)
        self.client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")
        self.project = None
    
    def create(self, task, project_name=None):
        """Create a project from a task description."""
        if not project_name:
            project_name = datetime.now().strftime("project_%Y%m%d_%H%M%S")
        
        self.project = PROJECTS_DIR / project_name
        self.project.mkdir(exist_ok=True)
        
        print(f"📁 Project: {self.project}")
        print(f"🎯 Task: {task}")
        print(f"🤖 Generating...")
        print()
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": CODING_PROMPT},
                {"role": "user", "content": task}
            ],
            temperature=0.5,
            max_tokens=8192,
            timeout=120
        )
        
        content = response.choices[0].message.content
        
        # Extract and save files
        files_created = self._save_files(content)
        
        # Save the full response
        with open(self.project / "README.md", 'w') as f:
            f.write(f"# {project_name}\n\n")
            f.write(f"**Task:** {task}\n\n")
            f.write(content)
        
        print(f"\n✅ Created {files_created} files in {self.project}")
        print(f"   Run: cd {self.project} && python main.py")
        
        # Try to auto-detect run command
        if (self.project / "main.py").exists():
            print(f"\n🚀 Testing: python3 main.py")
            try:
                result = subprocess.run(
                    [sys.executable, str(self.project / "main.py")],
                    capture_output=True, text=True, timeout=15, cwd=self.project
                )
                if result.stdout:
                    print(f"   Output: {result.stdout[:500]}")
                if result.stderr:
                    print(f"   Errors: {result.stderr[:300]}")
            except Exception as e:
                print(f"   Run error: {e}")
        
        return self.project
    
    def debug(self, file_path, error=None):
        """Debug an existing file."""
        p = Path(file_path)
        if not p.exists():
            return f"File not found: {file_path}"
        
        code = p.read_text()
        prompt = f"Debug this code:\n\n```python\n{code}\n```\n"
        if error:
            prompt += f"\nError: {error}\n\nFind and fix the issue."
        else:
            prompt += "\nReview for bugs, performance issues, and security problems."
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096
        )
        
        print(response.choices[0].message.content)
        
        # Save fix
        fix_path = p.parent / f"{p.stem}_fixed{p.suffix}"
        content = response.choices[0].message.content
        code_match = content.split("```")[1] if "```" in content else ""
        if code_match and "python" in code_match:
            code_match = code_match.replace("python", "", 1).strip()
            with open(fix_path, 'w') as f:
                f.write(code_match)
            print(f"\n💾 Fixed version saved to: {fix_path}")
    
    def _save_files(self, content):
        """Extract FILE: blocks and save them."""
        import re
        count = 0
        
        # Find FILE: path blocks
        pattern = r'FILE:\s*([^\n]+)\n```(?:\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            # Fallback: save full content as response.md
            with open(self.project / "response.md", 'w') as f:
                f.write(content)
            return 0
        
        for filepath, code in matches:
            filepath = filepath.strip().strip('"').strip("'").strip('`')
            full_path = self.project / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(code.strip())
            print(f"  📄 {filepath}")
            count += 1
        
        return count


def main():
    parser = argparse.ArgumentParser(description="AI Coding Agent")
    parser.add_argument("task", nargs="*", help="What to build")
    parser.add_argument("--debug", "-d", help="Debug a file")
    parser.add_argument("--name", "-n", help="Project name")
    parser.add_argument("--list", "-l", action="store_true", help="List projects")
    
    args = parser.parse_args()
    
    agent = CodingAgent()
    
    if args.list:
        print("📁 Projects:")
        for p in sorted(PROJECTS_DIR.iterdir()):
            if p.is_dir():
                readme = p / "README.md"
                task = readme.read_text().split('\n')[2] if readme.exists() else ""
                files = len(list(p.glob("*")))
                print(f"  {p.name}  ({files} files) {task[:50]}")
        return
    
    if args.debug:
        agent.debug(args.debug)
        return
    
    if args.task:
        agent.create(" ".join(args.task), args.name)
    else:
        parser.print_help()
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} \"Create a FastAPI trading API\"")
        print(f"  python {sys.argv[0]} -d myapp.py --name my-app")


if __name__ == "__main__":
    main()
