from app.llm.client import call_model


def run_serp_synthesis(payload: dict) -> dict:
    return call_model("serp_synthesis", "serp_synthesis_v1", payload)


def run_brief_generation(payload: dict) -> dict:
    return call_model("brief_generation", "brief_generation_v1", payload)
