import csv
from pathlib import Path


def import_gsc_csv(artifact_path: str) -> dict:
    path = Path(artifact_path)
    rows: list[dict] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            query = row.get("Query") or row.get("query")
            date = row.get("Date") or row.get("date")
            if not query or not date:
                continue
            rows.append(
                {
                    "query": query,
                    "page": row.get("Page") or row.get("page"),
                    "date": date,
                    "clicks": row.get("Clicks") or row.get("clicks"),
                    "impressions": row.get("Impressions") or row.get("impressions"),
                    "ctr": row.get("CTR") or row.get("ctr"),
                    "position": row.get("Position") or row.get("position"),
                }
            )

    return {"rows": rows, "source_path": str(path)}
