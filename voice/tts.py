#!/usr/bin/env python3
"""Bionic Voice - standalone, local text-to-speech (Kokoro-82M).

Intentionally Bionic-agnostic: a normal Python CLI that turns text into speech
with a local neural model, then plays it with `afplay`. Because it depends on
nothing Bionic-specific, future Bionic updates cannot break it. Bionic reaches
it only through a thin Skill + the shell.

Usage:
  tts.py "some text" [--voice bf_isabella|bf_emma|/path/voice.pt]
                     [--speed 1.0] [--no-play] [--out FILE] [--stdin]

Env:
  BIONIC_VOICE_ROOT   install root (default ~/.lmstudio/voice-engine)
"""
import argparse, os, sys, wave, subprocess
import numpy as np
import torch

ROOT = os.environ.get("BIONIC_VOICE_ROOT", os.path.expanduser("~/.lmstudio/voice-engine"))
MODEL_DIR = os.path.join(ROOT, "model")
SAMPLE_RATE = 24000
DEFAULT_VOICE = "bf_isabella"
# Kokoro voice ids begin with a language letter.
LANG_FOR_LETTER = {"a": "a", "b": "b", "e": "e", "f": "f",
                   "h": "h", "i": "i", "j": "j", "z": "z", "p": "p"}


def resolve_voice(voice: str) -> str:
    """Accept a voice id (bf_isabella) or a direct path to a .pt file."""
    if voice.endswith(".pt") or os.path.sep in voice:
        return voice
    return os.path.join(MODEL_DIR, "voices", voice + ".pt")


def render(text: str, voice_path: str, speed: float = 1.0) -> np.ndarray:
    from kokoro.model import KModel
    from kokoro import KPipeline
    voice_id = os.path.basename(voice_path)[:-3]
    lang = LANG_FOR_LETTER.get(voice_id[0], "b")
    model = KModel(
        config=os.path.join(MODEL_DIR, "config.json"),
        model=os.path.join(MODEL_DIR, "kokoro-v1_0.pth"),
    ).to("cpu").eval()
    pipe = KPipeline(lang_code=lang, model=model)
    chunks = []
    for item in pipe(text, voice=voice_path, speed=speed):
        tensors = [x for x in item if torch.is_tensor(x)]
        if tensors:
            chunks.append(tensors[0])
    audio = torch.cat(chunks, dim=-1).reshape(-1).cpu().numpy()
    return np.clip(audio, -1.0, 1.0)


def save_wav(path: str, audio: np.ndarray) -> None:
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser(description="Bionic Voice (local Kokoro TTS)")
    ap.add_argument("text", nargs="?", default=None, help="text to speak (omit to read stdin)")
    ap.add_argument("--voice", default=DEFAULT_VOICE,
                    help="voice id (bf_isabella, bf_emma) or path to a .pt file")
    ap.add_argument("--speed", type=float, default=1.0, help="speech speed 0.5-2.0")
    ap.add_argument("--no-play", action="store_true", help="render only, do not play")
    ap.add_argument("--out", default=None, help="WAV output path")
    ap.add_argument("--stdin", action="store_true", help="read text from stdin")
    args = ap.parse_args()

    text = args.text
    if args.stdin or text is None:
        text = sys.stdin.read()
    text = (text or "").strip()
    if not text:
        print("bionic-voice: no text to speak", file=sys.stderr)
        sys.exit(2)

    voice_path = resolve_voice(args.voice)
    if not os.path.exists(voice_path):
        print(f"bionic-voice: voice not found: {voice_path}", file=sys.stderr)
        sys.exit(3)

    audio = render(text, voice_path, args.speed)
    out = args.out or os.path.join(ROOT, "state", "last.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    save_wav(out, audio)
    print(os.path.abspath(out))
    if not args.no_play:
        subprocess.run(["afplay", out], check=False)


if __name__ == "__main__":
    main()
