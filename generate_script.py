from __future__ import annotations

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
TOPIC = "Linear Data Structures"


def generate_raw_script(subtopic: str) -> str:
    subtopic_clean = subtopic.title().strip()

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("Loading model on GPU...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    prompt = f"""
You are an educational content generator.

Generate a teaching script in JSON format.

Topic: {TOPIC}
Subtopic: {subtopic_clean}

Output JSON should use this structure:
{{
  "topic": "{TOPIC}",
  "subtopic": "{subtopic_clean}",
  "learning_objectives": ["string"],
  "scenes": [
    {{
      "scene_id": 1,
      "slide_title": "string",
      "narration": "string",
      "diagram_type": "string",
      "duration_seconds": 30
    }}
  ]
}}

Rules:
- Generate 4 to 6 scenes.
- Use simple, clear language for undergraduate students.
- Explain in great detail.
- Focus on explaining what {subtopic_clean} is, why it is used, its basic operations, time complexity, space complexity, merits, demerits, and applications.
- Do NOT include Learning Objectives.
- Do NOT include code blocks.
- Do NOT include markdown.
- Output only JSON.
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    print("Generating script...")
    outputs = model.generate(
        **inputs,
        max_new_tokens=1020,
        temperature=0.25,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    prompt_len = inputs["input_ids"].shape[1]
    gen_tokens = outputs[0][prompt_len:]
    decoded_output = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    return decoded_output