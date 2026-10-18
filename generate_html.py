from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, List


def paragraphize(text: str) -> List[str]:
    text = str(text).strip()
    if not text:
        return []
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return parts if parts else [text]


def generate_html_from_script(script: Dict[str, Any], output_path: str):
    topic = str(script.get("topic", "Educational Content")).strip()
    subtopic = str(script.get("subtopic", "Subtopic")).strip()
    objectives = script.get("learning_objectives", [])
    scenes = script.get("scenes", [])

    topic_html = escape(topic)
    subtopic_html = escape(subtopic)

    objectives_html = ""
    if objectives:
        items = "\n".join(
            f"<li>{escape(str(obj))}</li>"
            for obj in objectives
            if str(obj).strip()
        )
        objectives_html = f"""
        <section class="card">
            <h2>Learning Objectives</h2>
            <ul class="objectives">
                {items}
            </ul>
        </section>
        """

    scenes_html = ""
    for i, scene in enumerate(scenes, start=1):
        slide_title = escape(str(scene.get("slide_title", f"Part {i}")).strip())
        narration = str(scene.get("narration", "")).strip()

        paragraphs = paragraphize(narration)
        if not paragraphs:
            paragraphs = ["No content found."]

        narration_html = "\n".join(
            f"<p>{escape(p)}</p>" for p in paragraphs
        )

        scenes_html += f"""
        <section class="scene-card">
            <h3>{slide_title}</h3>
            <div class="scene-body">
                {narration_html}
            </div>
        </section>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_html} - {subtopic_html}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #1f2937;
        }}

        .container {{
            width: min(1100px, 92%);
            margin: 30px auto 60px;
        }}

        .hero {{
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            color: white;
            padding: 32px;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
            margin-bottom: 24px;
        }}

        .hero h1 {{
            margin: 0 0 8px;
            font-size: 2rem;
        }}

        .hero h2 {{
            margin: 0;
            font-size: 1.1rem;
            font-weight: normal;
            opacity: 0.95;
        }}

        .card, .scene-card {{
            background: white;
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        }}

        .card h2 {{
            margin-top: 0;
        }}

        .objectives {{
            margin: 0;
            padding-left: 22px;
        }}

        .objectives li {{
            margin-bottom: 8px;
            line-height: 1.6;
        }}

        .scene-card h3 {{
            margin-top: 0;
            margin-bottom: 14px;
            font-size: 1.35rem;
            color: #111827;
        }}

        .scene-body p {{
            line-height: 1.8;
            margin: 0 0 12px;
            font-size: 1rem;
        }}

        .scene-body p:last-child {{
            margin-bottom: 0;
        }}

        @media (max-width: 700px) {{
            .hero {{
                padding: 24px;
            }}

            .hero h1 {{
                font-size: 1.6rem;
            }}

            .scene-card h3 {{
                font-size: 1.15rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="hero">
            <h1>{topic_html}</h1>
            <h2>Subtopic: {subtopic_html}</h2>
        </header>

        {objectives_html}

        {scenes_html}
    </div>
</body>
</html>
"""

    Path(output_path).write_text(html, encoding="utf-8")