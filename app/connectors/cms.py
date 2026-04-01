from urllib.parse import urlparse

import httpx


def _wordpress_slug_from_url(target_url: str | None) -> str | None:
    if not target_url:
        return None
    path = urlparse(target_url).path.strip("/")
    if not path:
        return None
    return path.split("/")[-1]


def _publish_wordpress(project_id: str, payload: dict, config: dict, mode: str) -> dict:
    base_url = (config.get("base_url") or "").rstrip("/")
    username = config.get("username")
    application_password = config.get("application_password")

    missing = [
        name
        for name, value in [
            ("base_url", base_url),
            ("username", username),
            ("application_password", application_password),
        ]
        if not value
    ]
    if missing:
        raise ValueError(f"Missing WordPress config: {', '.join(missing)}")

    slug = _wordpress_slug_from_url(payload.get("target_url"))
    endpoint = f"{base_url}/wp-json/wp/v2/pages"
    body = {
        "title": payload.get("title") or slug or "SEO Pipeline Draft",
        "content": payload["content_markdown"],
        "status": "draft" if mode == "draft" else "publish",
    }
    if slug:
        body["slug"] = slug

    with httpx.Client(auth=(username, application_password), timeout=20.0) as client:
        response = client.post(endpoint, json=body)
        response.raise_for_status()
        data = response.json()

    return {
        "project_id": project_id,
        "provider": "wordpress",
        "status": "published",
        "mode": mode,
        "wordpress_id": data.get("id"),
        "wordpress_link": data.get("link"),
        "target_url": payload.get("target_url"),
    }


def publish_update(project_id: str, payload: dict, provider: str = "generic_rest", mode: str = "draft", config: dict | None = None) -> dict:
    config = config or {}
    if provider == "wordpress":
        return _publish_wordpress(project_id, payload, config, mode)

    return {
        "project_id": project_id,
        "provider": provider,
        "status": "not_implemented",
        "mode": mode,
        "payload": payload,
    }
