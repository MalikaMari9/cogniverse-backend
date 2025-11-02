from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ResultType(str, Enum):
    system = "system"
    emotion = "emotion"
    memory = "memory"
    corrosion = "corrosion"
    summary = "summary"
    position = "position" 


class ResultBase(BaseModel):
    projectagentid: Optional[int] = None
    scenarioid: int
    resulttype: ResultType
    sequence_no: Optional[int] = None
    confidence_score: Optional[float] = None
    resulttext: str
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class ResultCreate(ResultBase):
    pass

class ResultUpdate(BaseModel):
    resulttype: Optional[ResultType] = None
    sequence_no: Optional[Annotated[int, Field(ge=0)]] = None
    confidence_score: Optional[Annotated[float, Field(ge=0, le=1)]] = None
    resulttext: Optional[str] = None
    status: Optional[LifecycleStatus] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None

class ResultResponse(ResultBase):
    resultid: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
   
class SaveSimulationResultsRequest(BaseModel):
    scenarioid: int
    projectid: int
    simulation: Dict[str, Any] = {}
    logs: List[Dict[str, Any]] = []
    agentLogs: Dict[str, List[Dict[str, Any]]] = {}
    positions: List[Dict[str, Any]] = []  # 🧭 NEW


    class Config:
        from_attributes = True



        