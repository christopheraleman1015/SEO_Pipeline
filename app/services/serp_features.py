def summarize_serp_snapshot(snapshot: dict) -> dict:
    return {"cluster_id": snapshot.get("cluster_id"), "summary": "pending"}
