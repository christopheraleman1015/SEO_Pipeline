from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.opportunity_brief import OpportunityBrief
from app.schemas.opportunity_evidence import OpportunityEvidenceCreate, OpportunityEvidenceRead
from app.services.opportunity_evidence import (
    create_evidence_file,
    create_evidence_note,
    list_evidence_for_brief,
)

router = APIRouter(tags=["opportunity-evidence"])


@router.post("/opportunity-briefs/{brief_id}/evidence", response_model=OpportunityEvidenceRead)
def add_opportunity_evidence_note(
    brief_id: UUID,
    payload: OpportunityEvidenceCreate,
    db: Session = Depends(get_db),
) -> OpportunityEvidenceRead:
    brief = db.get(OpportunityBrief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Opportunity brief not found")

    evidence = create_evidence_note(
        db=db,
        opportunity_brief_id=str(brief_id),
        title=payload.title,
        content_text=payload.content_text,
        evidence_type=payload.evidence_type,
    )
    return evidence


@router.post("/opportunity-briefs/{brief_id}/evidence/file", response_model=OpportunityEvidenceRead)
async def add_opportunity_evidence_file(
    brief_id: UUID,
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> OpportunityEvidenceRead:
    brief = db.get(OpportunityBrief, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Opportunity brief not found")

    content = await file.read()
    evidence = create_evidence_file(
        db=db,
        opportunity_brief_id=str(brief_id),
        title=title,
        filename=file.filename or "evidence.txt",
        content=content,
    )
    return evidence


@router.get("/opportunity-briefs/{brief_id}/evidence", response_model=list[OpportunityEvidenceRead])
def list_opportunity_evidence(brief_id: UUID, db: Session = Depends(get_db)) -> list[OpportunityEvidenceRead]:
    return list_evidence_for_brief(db, str(brief_id))
