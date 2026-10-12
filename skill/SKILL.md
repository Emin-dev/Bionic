---
name: voice-output
display-name: Voice Output
description: "Use for any spoken voice output from Bionic: reading answers aloud, speaking a status/summary update, text-to-speech, or when the user says 'speak that', 'read it', or 'voice on/off'. Runs 100% locally (Kokoro), no cloud."
---

# Voice Output (local, Bionic-agnostic)

You can **speak**. Audio is produced by a bundled local neural engine (Kokoro-82M, warm British voice). It is 100% on-device (no internet) and **standalone** — Bionic updates cannot break it.

## State
Controlled by the flag file `__ROOT__/state/voice_on`, which contains `on` or `off` (default `on`).

## Behaviour (automated)
- **Flag `on` (default):** after you finish a *final* answer, **speak a short summary** of it — 2 to 4 natural sentences of the key points, like an orchestrator giving a lead a brief status update. **Do not** read out full text, code, tables, logs, or file contents — summarize only.
- **User says** "voice off" / "stop talking" / "shut up": write `off` to `__ROOT__/state/voice_on` and stop speaking for the session.
- **User says** "voice on" / "talk to me" / "resume": write `on` to `__ROOT__/state/voice_on` and resume.
- **User asks to read a specific thing** ("read that", "speak the summary of X"): speak that regardless of the flag.

## How to speak
Run via `shell_command`, passing the summary on stdin:

    __ROOT__/env/bin/python __ROOT__/voice/tts.py --voice bf_isabella --stdin <<'EOF'
    <your 2-4 sentence spoken summary>
    EOF

- Voices: `bf_isabella` (warm, default) and `bf_emma` (polished).
- The engine lives at `__ROOT__` (default `~/.lmstudio/voice-engine`). Do **not** edit the engine — just call `tts.py`.

## Resilience / self-heal
If the engine path is missing (e.g. after a reinstall or OS move), re-run the installer: `__ROOT__/install.sh`. Because the engine is standalone, this feature keeps working across Bionic updates.
