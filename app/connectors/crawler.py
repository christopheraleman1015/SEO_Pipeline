import csv
from pathlib import Path


def _pick(row: dict[str, str], *names: str) -> str | None:
    lowered = {key.strip().lower(): value for key, value in row.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value not in (None, ""):
            return value
    return None


def import_crawl_export(project_id: str, artifact_path: str) -> dict:
    path = Path(artifact_path)
    rows: list[dict] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            url = _pick(row, "Address", "URL")
            if not url:
                continue

            rows.append(
                {
                    "url": url,
                    "title": _pick(row, "Title 1", "Title"),
                    "h1": _pick(row, "H1-1", "H1 1", "H1"),
                    "meta_robots": _pick(row, "Meta Robots 1", "Meta Robots"),
                    "canonical_url": _pick(row, "Canonical Link Element 1", "Canonical"),
                    "http_status": _pick(row, "Status Code", "Status"),
                    "indexability": _pick(row, "Indexability"),
                    "indexability_status": _pick(row, "Indexability Status"),
                    "word_count": _pick(row, "Word Count"),
                }
            )

    return {"project_id": project_id, "pages": rows, "source_path": str(path)}
