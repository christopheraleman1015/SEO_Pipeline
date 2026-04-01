from app.llm.prompts import PROMPTS


def call_model(task_type: str, prompt_version: str, payload: dict) -> dict:
    return {
        "task_type": task_type,
        "prompt": PROMPTS[prompt_version],
        "payload": payload,
        "status": "not_implemented",
    }
