from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from TTS.api import TTS


MODEL_NAME = "tts_models/en/ljspeech/tacotron2-DDC"
_tts = None


def load_tts():
    global _tts
    if _tts is None:
        print("Loading TTS model...")
        _tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)


def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name).strip("_")


def build_scene_text(scene: Dict[str, Any]) -> str:
    title = str(scene.get("slide_title", "")).strip()
    narration = str(scene.get("narration", "")).strip()

    if title and narration:
        return f"{title}. {narration}"
    if narration:
        return narration
    return title


def generate_scene_audios(script: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Generate one audio file per scene.
    Returns list of generated audio file paths.
    """
    load_tts()

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio_files: List[str] = []

    scenes = script.get("scenes", [])
    for i, scene in enumerate(scenes, start=1):
        text = build_scene_text(scene).strip()
        if not text:
            continue

        title = safe_filename(str(scene.get("slide_title", f"scene_{i}")))
        audio_path = out_dir / f"scene_{i:03d}_{title}.wav"

        print(f"Generating audio for Scene {i}...")
        _tts.tts_to_file(text=text, file_path=str(audio_path))

        audio_files.append(str(audio_path))

    return audio_files


def generate_full_audio(script: Dict[str, Any], output_file: str) -> str:
    """
    Generate one single audio file for the full script.
    """
    load_tts()

    parts: List[str] = []

    topic = str(script.get("topic", "")).strip()
    subtopic = str(script.get("subtopic", "")).strip()

    if topic:
        parts.append(topic)
    if subtopic:
        parts.append(f"Subtopic: {subtopic}")

    objectives = script.get("learning_objectives", [])
    if objectives:
        parts.append("Learning objectives.")
        for obj in objectives:
            obj_text = str(obj).strip()
            if obj_text:
                parts.append(obj_text)

    for scene in script.get("scenes", []):
        scene_text = build_scene_text(scene)
        if scene_text:
            parts.append(scene_text)

    full_text = " ".join(parts).strip()
    if not full_text:
        raise ValueError("No text found in script for audio generation.")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Generating full narration audio...")
    _tts.tts_to_file(text=full_text, file_path=str(output_path))

    return str(output_path)


def main():
    import json

    subtopic = input("Enter subtopic (e.g., linked_list): ").strip().lower().replace(" ", "_")
    if not subtopic:
        print("No subtopic entered. Exiting.")
        return

    json_path = Path(f"outputs/json/script_{subtopic}.json")
    if not json_path.exists():
        raise FileNotFoundError(f"Could not find {json_path}")

    script = json.loads(json_path.read_text(encoding="utf-8"))

    audio_dir = Path("outputs/audio") / subtopic
    full_audio_path = Path("outputs/audio") / f"{subtopic}_full.wav"

    generate_scene_audios(script, str(audio_dir))
    generate_full_audio(script, str(full_audio_path))

    print(f"Scene audios saved in: {audio_dir}")
    print(f"Full audio saved as: {full_audio_path}")


if __name__ == "__main__":
    main()