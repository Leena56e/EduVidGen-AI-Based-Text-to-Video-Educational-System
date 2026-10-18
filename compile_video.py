from __future__ import annotations

import subprocess
import wave
from pathlib import Path
from typing import List


FFMPEG = "ffmpeg"


def get_wav_duration_seconds(wav_path: Path) -> float:
    """
    Get duration of a WAV file in seconds using the built-in wave module.
    """
    with wave.open(str(wav_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        if rate == 0:
            return 0.0
        return frames / float(rate)


def natural_sort_key(path: Path):
    """
    Sort files like frame_001, frame_002, ..., frame_010 correctly.
    """
    return path.name


def run_ffmpeg(command: List[str]):
    """
    Run ffmpeg command and raise error if it fails.
    """
    print("Running:", " ".join(command))
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("FFmpeg command failed.")


def build_scene_video(image_path: Path, audio_path: Path, output_path: Path):
    duration = get_wav_duration_seconds(audio_path)

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
               "pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]

    run_ffmpeg(command)

def concat_clips(clip_paths: List[Path], output_video: Path, temp_dir: Path):
    """
    Concatenate clips WITH audio correctly (re-encode).
    """
    concat_file = temp_dir / "concat_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clip_paths:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        str(output_video),
    ]

    run_ffmpeg(command)


def compile_video_for_subtopic(subtopic: str):
    """
    Compile scene frames + scene audios into one final mp4 video.
    """
    subtopic_tag = subtopic.strip().lower().replace(" ", "_")

    frames_dir = Path("outputs/frames") / subtopic_tag
    audio_dir = Path("outputs/audio") / subtopic_tag
    temp_dir = Path("outputs/temp_video") / subtopic_tag
    video_dir = Path("outputs/video")
    output_video = video_dir / f"{subtopic_tag}.mp4"

    if not frames_dir.exists():
        raise FileNotFoundError(f"Frames folder not found: {frames_dir}")

    if not audio_dir.exists():
        raise FileNotFoundError(f"Audio folder not found: {audio_dir}")

    temp_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    frame_files = sorted(frames_dir.glob("frame_*.png"), key=natural_sort_key)
    audio_files = sorted(audio_dir.glob("scene_*.wav"), key=natural_sort_key)

    if not frame_files:
        raise FileNotFoundError(f"No frame images found in: {frames_dir}")

    if not audio_files:
        raise FileNotFoundError(f"No scene audio files found in: {audio_dir}")

    scene_count = min(len(frame_files), len(audio_files))
    print(f"Found {len(frame_files)} frames and {len(audio_files)} audio files.")
    print(f"Using {scene_count} matched scenes for compilation.")

    temp_clips: List[Path] = []

    for i in range(scene_count):
        frame = frame_files[i]
        audio = audio_files[i]
        temp_clip = temp_dir / f"clip_{i + 1:03d}.mp4"

        print(f"Creating clip {i + 1}:")
        print(f"  Frame: {frame.name}")
        print(f"  Audio: {audio.name}")

        build_scene_video(frame, audio, temp_clip)
        temp_clips.append(temp_clip)

    print("\nConcatenating all clips into final video...")
    concat_clips(temp_clips, output_video, temp_dir)

    print(f"\nFinal video created: {output_video}")


def main():
    subtopic = input("Enter subtopic (e.g., stack, queue, linked_list): ").strip()
    if not subtopic:
        print("No subtopic entered. Exiting.")
        return

    try:
        compile_video_for_subtopic(subtopic)
    except Exception as e:
        print(f"\nVideo compilation failed: {e}")


if __name__ == "__main__":
    main()