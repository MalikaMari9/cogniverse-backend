from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field



class AgentCustomization(BaseModel):
    slot: int = Field(..., ge=0, le=4)
    name: Optional[str] = None
    role: Optional[str] = None
    persona: Optional[str] = None
    cognitive_bias: Optional[str] = Field(default=None, alias="cognitiveBias")
    emotional_state: Optional[str] = Field(default=None, alias="emotionalState")
    mbti: Optional[str] = None
    motivation: Optional[str] = None
    skills: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    quirks: Optional[List[str]] = None
    biography: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


class RelationshipSeed(BaseModel):
    from_slot: int = Field(..., alias="from_slot", ge=0, le=4)
    to_slot: int = Field(..., alias="to_slot", ge=0, le=4)
    strength: float = Field(..., ge=-1.0, le=1.0)

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


class SimulationCreateRequest(BaseModel):
    scenario: str
    custom_agents: Optional[List[AgentCustomization]] = Field(
        default=None, alias="custom_agents"
    )
    agent_profiles: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="agent_profiles"
    )
    relationships: Optional[List[RelationshipSeed]] = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


class SimulationAdvanceRequest(BaseModel):
    steps: int = Field(default=1, ge=1, le=50)


class SimulationFateRequest(BaseModel):
    prompt: Optional[str] = None


class SimulationResponse(BaseModel):
    simulation: Dict[str, Any]

    class Config:
        extra = "allow"
