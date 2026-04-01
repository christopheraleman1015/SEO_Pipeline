from uuid import UUID

from pydantic import BaseModel


class SERPSummary(BaseModel):
    cluster_id: UUID | str
    primary_intent: str
    dominant_page_type: str
    freshness_sensitivity: str
    common_sections: list[str]
    common_entities: list[str]
    trust_signals: list[str]
    content_gaps: list[str]
    recommended_strategy: str


class ContentBrief(BaseModel):
    cluster_id: UUID | str
    target_query: str
    target_page_type: str
    page_goal: str
    audience: str
    title_options: list[str]
    h1_options: list[str]
    must_cover_sections: list[str]
    entities_to_cover: list[str]
    internal_links_in: list[str]
    internal_links_out: list[str]
    schema_types: list[str]
    differentiator: str
    evidence_required: list[str]
    risks: list[str]
