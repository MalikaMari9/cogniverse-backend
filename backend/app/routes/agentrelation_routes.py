from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.controllers import agentrelation_controller
from app.db.schemas.agentrelation_schema import AgentRelationCreate, AgentRelationUpdate, AgentRelationResponse

router = APIRouter(prefix="/agent-relations", tags=["Agent Relations"])


@router.get("/", response_model=List[AgentRelationResponse])
def get_all(db: Session = Depends(get_db)):
    return agentrelation_controller.get_all_relations(db)


@router.get("/{agentRelationID}", response_model=AgentRelationResponse)
def get_by_id(agentRelationID: int, db: Session = Depends(get_db)):
    return agentrelation_controller.get_relation_by_id(db, agentRelationID)


@router.post("/", response_model=AgentRelationResponse, status_code=201)
def create(relation: AgentRelationCreate, db: Session = Depends(get_db)):
    return agentrelation_controller.create_relation(db, relation)


@router.put("/{agentRelationID}", response_model=AgentRelationResponse)
def update(agentRelationID: int, relation: AgentRelationUpdate, db: Session = Depends(get_db)):
    return agentrelation_controller.update_relation(db, agentRelationID, relation)


@router.delete("/{agentRelationID}")
def delete(agentRelationID: int, db: Session = Depends(get_db)):
    return agentrelation_controller.delete_relation(db, agentRelationID)
