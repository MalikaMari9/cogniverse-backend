from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.controllers import agent_controller
from app.db.database import get_db

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=List[AgentResponse])
def get_all_agents(db: Session = Depends(get_db)):
    return agent_controller.get_all_agents(db)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    return agent_controller.get_agent_by_id(agent_id, db)


@router.post("/", response_model=AgentResponse, status_code=201)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_controller.create_agent(agent, db)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    return agent_controller.update_agent(agent_id, agent, db)


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    return agent_controller.delete_agent(agent_id, db)
