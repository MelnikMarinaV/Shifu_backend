import json
import requests


def check_text_with_ollama(transcript: str, task_text: str) -> dict:
    prompt = f"""
Ты преподаватель китайского языка.

Задание: {task_text}
Ответ ученика: {transcript}

Оцени ответ от 0 до 100 и дай комментарий.

Ответ верни строго в JSON:
{{
  "score": число,
  "feedback": "текст"
}}
"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "score": {"type": "integer"},
                    "feedback": {"type": "string"},
                    "short_comment": {"type": "string"},
                },
                "required": ["score", "feedback", "short_comment"],
            },
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return json.loads(data["message"]["content"])
