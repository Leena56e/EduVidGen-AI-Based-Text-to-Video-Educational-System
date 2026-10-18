from __future__ import annotations

import json
from pathlib import Path

from generate_script import TOPIC, generate_raw_script
from repair_raw_output import repair_raw_text_to_script
from generate_html import generate_html_from_script
from generate_snapshots import capture_snapshots_from_html
from generate_audio import generate_scene_audios, generate_full_audio
from compile_video import compile_video_for_subtopic


OUTPUT_DIR = Path("outputs")
RAW_DIR = OUTPUT_DIR / "raw"
JSON_DIR = OUTPUT_DIR / "json"
HTML_DIR = OUTPUT_DIR / "html"


def ensure_output_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def main():
    subtopic = input("Enter linear data structure (e.g., Stack, Queue, Linked List): ").strip()
    if not subtopic:
        print("No subtopic entered. Exiting.")
        return

    ensure_output_dirs()

    subtopic_clean = subtopic.title().strip()
    subtopic_tag = safe_filename(subtopic_clean)

    raw_file = RAW_DIR / f"raw_output_{subtopic_tag}.txt"
    json_file = JSON_DIR / f"script_{subtopic_tag}.json"
    html_file = HTML_DIR / f"{subtopic_tag}.html"

    try:
        print(f"\nGenerating content for: {TOPIC} -> {subtopic_clean}")

        raw_output = generate_raw_script(subtopic_clean)
        raw_file.write_text(raw_output, encoding="utf-8")
        print(f"Raw output saved to: {raw_file}")

        script_data = repair_raw_text_to_script(
            raw_text=raw_output,
            fallback_topic=TOPIC,
            fallback_subtopic=subtopic_clean
        )
        json_file.write_text(
            json.dumps(script_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"Repaired JSON saved to: {json_file}")

        generate_html_from_script(script_data, str(html_file))
        print(f"HTML generated successfully: {html_file}")
        frame_dir = f"outputs/frames/{subtopic_tag}"

        capture_snapshots_from_html(
            html_file=str(html_file),
            output_dir=frame_dir
        )

        print(f"Snapshots saved in: {frame_dir}")
        audio_dir = f"outputs/audio/{subtopic_tag}"
        full_audio_file = f"outputs/audio/{subtopic_tag}_full.wav"

        scene_audio_files = generate_scene_audios(script_data, audio_dir)
        print(f"Scene audios saved in: {audio_dir}")

        generate_full_audio(script_data, full_audio_file)
        print(f"Full audio saved as: {full_audio_file}")

        # Compile video from frames + audio
        compile_video_for_subtopic(subtopic_tag)
        print(f"Video compiled successfully: outputs/video/{subtopic_tag}.mp4")

        print("\nDone.")

    except Exception as e:
        print(f"\nPipeline failed: {e}")


if __name__ == "__main__":
    main()