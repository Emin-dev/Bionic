# Bionic Voice

Give **Bionic** a **warm British voice** that speaks a short summary of every
answer — **100% local, private, no cloud.**

Built on the open-source [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
neural TTS model. Runs entirely on your Mac (Apple Silicon or Intel).

## One-button install (free)

    curl -fsSL https://raw.githubusercontent.com/Emin-dev/Bionic/main/install.sh | bash

Or clone:

    git clone https://github.com/Emin-dev/Bionic.git ~/.lmstudio/voice-engine
    cd ~/.lmstudio/voice-engine && ./install.sh

The installer: installs `uv` (if missing), builds a Python venv with pinned
deps, downloads the ~312 MB Kokoro model, deploys a **Skill** into Bionic, and
self-tests with an audio sample. Then **start a new Bionic session.**

> Replace `Emin-dev` with whoever publishes this repo.

## How it works (and why it survives Bionic updates)

Two pieces, deliberately separated:

1. **Standalone engine** — `voice/tts.py` + a local model. A normal Python CLI
   (`text -> speech -> afplay`). It depends on *nothing* Bionic-specific, so
   Bionic updates cannot break it.
2. **Thin Skill** — `skill/SKILL.md`, deployed to `~/.lmstudio/skills/voice-output/`.
   This is the only touchpoint with Bionic: it tells the agent to read a short
   spoken summary of its answers via `tts.py`.

Because Bionic talks to the engine only through the shell + a small markdown
skill (both stable, simple surfaces), the feature keeps working as Bionic
evolves. If anything is ever missing, just re-run `./install.sh` (idempotent).

## Using it in Bionic

- **On by default** — after each final answer, I speak a 2-4 sentence summary
  (an orchestrator-style status update), not the full text/code.
- **Turn off:** say "voice off". **Turn on:** say "voice on".
- **Read a specific thing:** say "read that" / "speak the summary of X".
- **Choose a voice:** `bf_isabella` (warm, default) or `bf_emma` (polished).

## Manual / headless use

    ~/.lmstudio/voice-engine/env/bin/python ~/.lmstudio/voice-engine/voice/tts.py \
      --voice bf_isabella --speed 1.0 "Hello from the command line."
    echo "any text" | ~/.lmstudio/voice-engine/env/bin/python \
      ~/.lmstudio/voice-engine/voice/tts.py --stdin

## Requirements & notes

- macOS (`afplay`) for playback. Python is handled via `uv` (auto-installed).
- The model + venv live in `~/.lmstudio/voice-engine/` (`env/`, `model/`,
  `state/` are generated and git-ignored; the repo is small).
- First synthesis of a voice loads the model (~5-8 s); subsequent reads are quick.

## Troubleshooting

- **Hear nothing:** check your macOS output device. The engine prints the WAV path.
- **`uv` errors:** re-run `install.sh` (it re-creates the venv).
- **Re-install / repair:** `~/.lmstudio/voice-engine/install.sh`
- **Uninstall:** delete `~/.lmstudio/voice-engine/` and `~/.lmstudio/skills/voice-output/`.

## License

MIT — free to use, modify, and redistribute. The Kokoro-82M model is Apache-2.0.
