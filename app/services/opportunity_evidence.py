from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.opportunity_brief import OpportunityBrief
from app.models.opportunity_evidence import OpportunityEvidence
from app.services.artifacts import create_artifact_record
from app.utils.ids import as_uuid


def create_evidence_note(
    db: Session,
    opportunity_brief_id: str,
    title: str,
    content_text: str,
    evidence_type: str = "note",
) -> OpportunityEvidence:
    brief = db.get(OpportunityBrief, as_uuid(opportunity_brief_id))
    if not brief:
        raise ValueError("Opportunity brief not found")

    evidence = OpportunityEvidence(
        project_id=brief.project_id,
        opportunity_brief_id=brief.id,
        artifact_id=None,
        evidence_type=evidence_type,
        title=title,
        content_text=content_text,
        metadata_json={},
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def create_evidence_file(
    db: Session,
    opportunity_brief_id: str,
    title: str,
    filename: str,
    content: bytes,
    evidence_type: str = "file",
) -> OpportunityEvidence:
    brief = db.get(OpportunityBrief, as_uuid(opportunity_brief_id))
    if not brief:
        raise ValueError("Opportunity brief not found")

    artifact = create_artifact_record(
        db=db,
        project_id=brief.project_id,
        artifact_type="evidence",
        source_name=filename,
        content=content,
    )
    evidence = OpportunityEvidence(
        project_id=brief.project_id,
        opportunity_brief_id=brief.id,
        artifact_id=artifact.id,
        evidence_type=evidence_type,
        title=title,
        content_text=None,
        metadata_json={"filename": filename, "artifact_id": str(artifact.id)},
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def list_evidence_for_brief(db: Session, opportunity_brief_id: str) -> list[OpportunityEvidence]:
    return list(
        db.scalars(
            select(OpportunityEvidence).where(
                OpportunityEvidence.opportunity_brief_id == as_uuid(opportunity_brief_id)
            )
        ).all()
    )
