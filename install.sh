#!/usr/bin/env bash
# Bionic Voice — one-button installer. Works on a fresh Mac. Idempotent (re-runnable).
set -euo pipefail

# Public repo URL. Replace Emin-dev with the real one before sharing the curl one-liner.
REPO_URL="${BIONIC_VOICE_REPO:-https://github.com/Emin-dev/Bionic.git}"

ROOT="${BIONIC_VOICE_ROOT:-$HOME/.lmstudio/voice-engine}"
export BIONIC_VOICE_ROOT="$ROOT"
export PATH="$HOME/.local/bin:$PATH"

say(){ printf '\033[1;36m==> %s\033[0m\n' "$*"; }

# Locate source files (from a clone, or clone first if piped via curl|bash).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -f "${SCRIPT_DIR:-/nonexistent}/voice/tts.py" ]; then
  SRC="$SCRIPT_DIR"
else
  say "Run via curl|bash - cloning $REPO_URL into $ROOT"
  rm -rf "$ROOT"
  git clone --depth 1 "$REPO_URL" "$ROOT"
  SRC="$ROOT"
fi

say "Installing Bionic Voice into $ROOT"

# 1) uv (fast Python package manager)
if ! command -v uv >/dev/null 2>&1; then
  say "uv not found - installing"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# 2) venv + pinned dependencies
cd "$ROOT"
uv venv env --python 3.11
export VIRTUAL_ENV="$ROOT/env"
uv pip install --python "$ROOT/env/bin/python" -r "$SRC/requirements.txt"

# 3) English phoneme model (pre-install so the runtime never shells out to uv)
"$ROOT/env/bin/python" - <<'PYBLOCK'
import spacy.util
if not spacy.util.is_package("en_core_web_sm"):
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
print("spacy en_core_web_sm ready")
PYBLOCK

# 4) Kokoro model + voices (plain curl; bypasses the HF Xet/uv download path)
mkdir -p "$ROOT/model/voices"
B="https://huggingface.co/hexgrad/Kokoro-82M/resolve/main"
[ -f "$ROOT/model/kokoro-v1_0.pth" ] || { say "downloading Kokoro-82M model (~312 MB)"; curl -fL "$B/kokoro-v1_0.pth" -o "$ROOT/model/kokoro-v1_0.pth"; }
[ -f "$ROOT/model/config.json" ]     || curl -fL "$B/config.json" -o "$ROOT/model/config.json"
for v in bf_isabella bf_emma; do
  [ -f "$ROOT/model/voices/$v.pt" ] || curl -fL "$B/voices/$v.pt" -o "$ROOT/model/voices/$v.pt"
done

# 5) deploy the Bionic skill (the only integration point; survives Bionic updates)
SKILL_HOME="$HOME/.lmstudio/skills/voice-output"
mkdir -p "$SKILL_HOME"
sed "s#__ROOT__#$ROOT#g" "$SRC/skill/SKILL.md" > "$SKILL_HOME/SKILL.md"

# 6) state flag (default: auto-speak ON)
mkdir -p "$ROOT/state"
[ -f "$ROOT/state/voice_on" ] || echo "on" > "$ROOT/state/voice_on"

# 7) self-test (you should hear a short sample)
say "self-test - you should hear a short voice sample"
"$ROOT/env/bin/python" "$ROOT/voice/tts.py" --voice bf_isabella --stdin <<'PYBLOCK'
Bionic Voice is installed and running locally. Hello.
PYBLOCK

echo
say "Done. Start a NEW Bionic session - I'll speak a short summary of my answers."
say "Toggle:   echo off > $ROOT/state/voice_on   (or just tell me: voice off)"
