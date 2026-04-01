from app.config import get_settings


def should_call_llm(task_type: str, priority_score: float, cache_hit: bool) -> bool:
    settings = get_settings()
    if cache_hit:
        return False
    if task_type == "serp_synthesis" and priority_score < settings.serp_priority_threshold:
        return False
    if task_type == "brief_generation" and priority_score < settings.brief_priority_threshold:
        return False
    return True


def select_model(task_type: str) -> str | None:
    settings = get_settings()
    if task_type in {"serp_synthesis", "brief_generation"}:
        return settings.llm_strong_model or settings.llm_default_model
    return settings.llm_cheap_model or settings.llm_default_model
