from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


def extract_json_region(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")

    match = re.search(r"```json\s*(\{.*?\})\s*```", t, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    if "{" in t and "}" in t:
        return t[t.find("{"): t.rfind("}") + 1].strip()

    return t.strip()


def normalize_json_text(text: str) -> str:
    t = text.strip()
    t = t.replace("“", '"').replace("”", '"').replace("’", "'")
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return t


def try_json_load(text: str) -> Optional[Dict[str, Any]]:
    candidate = normalize_json_text(extract_json_region(text))
    try:
        obj = json.loads(candidate)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def salvage_scenes_with_regex(text: str) -> Optional[Dict[str, Any]]:
    t = text.replace("\r\n", "\n").replace("\r", "\n")

    topic_match = re.search(r'"topic"\s*:\s*"([^"]+)"', t)
    subtopic_match = re.search(r'"subtopic"\s*:\s*"([^"]+)"', t)

    topic = topic_match.group(1) if topic_match else "Linear Data Structures"
    subtopic = subtopic_match.group(1) if subtopic_match else "Unknown Subtopic"

    titles = re.findall(r'"slide_title"\s*:\s*"([^"]+)"', t)
    narrations = re.findall(r'"narration"\s*:\s*"([^"]+)"', t)

    if not titles:
        titles = re.findall(r'"title"\s*:\s*"([^"]+)"', t)

    if not titles or not narrations:
        return None

    count = min(len(titles), len(narrations))
    scenes: List[Dict[str, Any]] = []

    for i in range(count):
        scenes.append({
            "scene_id": i + 1,
            "slide_title": titles[i],
            "narration": narrations[i],
            "diagram_type": "unknown",
            "duration_seconds": 30
        })

    return {
        "topic": topic,
        "subtopic": subtopic,
        "learning_objectives": [],
        "scenes": scenes
    }


def fallback_paragraph_to_scenes(raw_text: str, fallback_topic: str, fallback_subtopic: str) -> Dict[str, Any]:
    blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
    scenes: List[Dict[str, Any]] = []

    for i, block in enumerate(blocks[:6], start=1):
        scenes.append({
            "scene_id": i,
            "slide_title": f"{fallback_subtopic} (Part {i})",
            "narration": block,
            "diagram_type": "none",
            "duration_seconds": 30
        })

    return {
        "topic": fallback_topic,
        "subtopic": fallback_subtopic,
        "learning_objectives": [],
        "scenes": scenes
    }


def validate_script(script: Dict[str, Any], fallback_topic: str, fallback_subtopic: str) -> Dict[str, Any]:
    script.setdefault("topic", fallback_topic)
    script.setdefault("subtopic", fallback_subtopic)
    script.setdefault("learning_objectives", [])
    script.setdefault("scenes", [])

    if not isinstance(script["learning_objectives"], list):
        script["learning_objectives"] = []

    if not isinstance(script["scenes"], list):
        script["scenes"] = []

    cleaned_scenes = []
    for i, scene in enumerate(script["scenes"], start=1):
        if not isinstance(scene, dict):
            continue

        duration_value = scene.get("duration_seconds", 30)
        try:
            duration_value = int(duration_value)
        except (TypeError, ValueError):
            duration_value = 30

        cleaned_scenes.append({
            "scene_id": scene.get("scene_id", i),
            "slide_title": str(scene.get("slide_title", f"Scene {i}")).strip(),
            "narration": str(scene.get("narration", "")).strip(),
            "diagram_type": str(scene.get("diagram_type", "unknown")).strip(),
            "duration_seconds": duration_value
        })

    script["scenes"] = cleaned_scenes
    return script


def repair_raw_text_to_script(raw_text: str, fallback_topic: str, fallback_subtopic: str) -> Dict[str, Any]:
    script = try_json_load(raw_text)

    if script is None:
        script = salvage_scenes_with_regex(raw_text)

    if script is None:
        script = fallback_paragraph_to_scenes(raw_text, fallback_topic, fallback_subtopic)

    script = validate_script(script, fallback_topic, fallback_subtopic)
    return script