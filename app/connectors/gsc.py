def import_gsc_data(project_id: str, date_from: str | None, date_to: str | None) -> dict:
    return {"project_id": project_id, "date_from": date_from, "date_to": date_to, "rows": 0}
