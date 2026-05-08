#!/bin/bash
# ai — One command for all AI capabilities
# Add to ~/.bashrc: source /path/to/ai-pipeline/setup.sh

export AI_PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ai() {
    local cmd=$1
    shift
    
    case "$cmd" in
        chat|code|media|model)
            python3 "$AI_PIPELINE_DIR/ai.py" "$cmd" "$@"
            ;;
        *)
            echo "AI Pipeline — Usage:"
            echo "  ai chat <question>    — Chat with AI (like Claude)"
            echo "  ai code <task>        — Coding agent (like Cursor)"
            echo "  ai media --script ... — Create videos/images/music"
            echo "  ai model status       — Check local models"
            echo ""
            echo "Set DEEPSEEK_API_KEY in your environment"
            ;;
    esac
}

# Auto-completion
_ai_complete() {
    local cur="${COMP_WORDS[1]}"
    local cmds="chat code media model"
    COMPREPLY=($(compgen -W "$cmds" -- "$cur"))
}
complete -F _ai_complete ai 2>/dev/null
