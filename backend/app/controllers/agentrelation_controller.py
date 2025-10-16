from sqlalchemy.orm import Session
from sqlalchemy import or_, and_   # ← add these
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.db.models.agentrelation_model import AgentRelation
from app.db.schemas.agentrelation_schema import AgentRelationCreate, AgentRelationUpdate


def get_all_relations(db: Session):
    return db.query(AgentRelation).all()


def get_relation_by_id(db: Session, agentrelationid: int):
    relation = db.query(AgentRelation).filter(AgentRelation.agentrelationid == agentrelationid).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")
    return relation


def create_relation(db: Session, relation_data: AgentRelationCreate):
    a_id = relation_data.agenta_id
    b_id = relation_data.agentb_id
    project_id = relation_data.projectid

    # Optional but recommended: canonicalize so smaller ID is always A
    relatob = relation_data.relationatob
    relbtoa = relation_data.relationbtoa
    if a_id > b_id:
        a_id, b_id = b_id, a_id
        relatob, relbtoa = relbtoa, relatob

    # Check existence regardless of input order
    existing = (
        db.query(AgentRelation)
        .filter(
            AgentRelation.projectid == project_id,
            or_(
                and_(AgentRelation.agenta_id == a_id, AgentRelation.agentb_id == b_id),
                and_(AgentRelation.agenta_id == b_id, AgentRelation.agentb_id == a_id),
            ),
        )
        .first()
    )

    if existing:
        # Update both directions on the single row
        # If you canonicalized, existing may be stored a<=b already; just assign the weights correctly
        existing.relationatob = relatob
        existing.relationbtoa = relbtoa
        existing.return_state = relation_data.return_state
        existing.status = relation_data.status
        db.commit()
        db.refresh(existing)
        return existing

    # Create new (using canonicalized order/weights)
    new_relation = AgentRelation(
        projectid=project_id,
        agenta_id=a_id,
        agentb_id=b_id,
        relationatob=relatob,
        relationbtoa=relbtoa,
        return_state=relation_data.return_state,
        status=relation_data.status,
    )
    db.add(new_relation)
    try:
        db.commit()
    except IntegrityError:
        # Race condition: someone inserted the reverse in between check and insert.
        db.rollback()
        # Fetch and update instead
        existing = (
            db.query(AgentRelation)
            .filter(
                AgentRelation.projectid == project_id,
                or_(
                    and_(AgentRelation.agenta_id == a_id, AgentRelation.agentb_id == b_id),
                    and_(AgentRelation.agenta_id == b_id, AgentRelation.agentb_id == a_id),
                ),
            )
            .first()
        )
        if existing:
            existing.relationatob = relatob
            existing.relationbtoa = relbtoa
            existing.return_state = relation_data.return_state
            existing.status = relation_data.status
            db.commit()
            db.refresh(existing)
            return existing
        # If somehow still not there, re-raise
        raise
    db.refresh(new_relation)
    return new_relation


def delete_relation(db: Session, agentrelationid: int):
    relation = db.query(AgentRelation).filter(AgentRelation.agentrelationid == agentrelationid).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    db.delete(relation)
    db.commit()
    return {"detail": "Relation deleted successfully"}