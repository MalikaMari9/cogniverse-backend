from sqlalchemy.orm import Session
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
    existing = (
        db.query(AgentRelation)
        .filter(
            AgentRelation.projectid == relation_data.projectid,
            AgentRelation.agenta_id == relation_data.agenta_id,
            AgentRelation.agentb_id == relation_data.agentb_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Relation already exists")

    new_relation = AgentRelation(**relation_data.dict())
    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)
    return new_relation


def update_relation(db: Session, agentrelationid: int, relation_data: AgentRelationUpdate):
    relation = db.query(AgentRelation).filter(AgentRelation.agentrelationid == agentrelationid).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    for key, value in relation_data.dict(exclude_unset=True).items():
        setattr(relation, key, value)

    db.commit()
    db.refresh(relation)
    return relation


def delete_relation(db: Session, agentrelationid: int):
    relation = db.query(AgentRelation).filter(AgentRelation.agentrelationid == agentrelationid).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Relation not found")

    db.delete(relation)
    db.commit()
    return {"detail": "Relation deleted successfully"}