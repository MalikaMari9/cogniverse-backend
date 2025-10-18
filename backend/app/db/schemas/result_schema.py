from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ResultType(str, Enum):
    text = "text"
    summary = "summary"
    log = "log"
    thought = "thought"

class ResultBase(BaseModel):
    projectagentid: int
    scenarioid: int
    resulttype: ResultType
    sequence_no: Annotated[int, Field(ge=0, description="Sequence number must be ≥ 0")]
    confidence_score: Annotated[float, Field(ge=0, le=1, description="Confidence between 0 and 1")]
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

class ResultResponse(ResultBase):
    resultid: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True