import json
import re

from ai_client import generate_text


def _extract_json(text):
    text = text.strip()

    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    # Find JSON array
    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def generate_quiz(text, count=3):
    prompt = f"""
Create a quiz based on the following text.

TEXT:
{text}

Create exactly {count} multiple-choice questions.

IMPORTANT:
Return ONLY valid JSON.
Do not use markdown.
Do not use ```json.
Do not add explanations outside the JSON.

Use exactly this format:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A"
  }}
]
"""

    response = generate_text(prompt)

    quiz = _extract_json(response)

    if not isinstance(quiz, list):
        raise RuntimeError("Gemini returned invalid quiz JSON.")

    if len(quiz) == 0:
        raise RuntimeError("Gemini returned an empty quiz.")

    cleaned_quiz = []

    for item in quiz:
        if not isinstance(item, dict):
            continue

        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")

        if not question:
            continue

        if not isinstance(options, list):
            continue

        if len(options) != 4:
            continue

        if not answer:
            continue

        cleaned_quiz.append({
            "question": question,
            "options": options,
            "answer": answer,
        })

    if not cleaned_quiz:
        raise RuntimeError("Gemini returned invalid quiz JSON.")

    return cleaned_quiz[:count]