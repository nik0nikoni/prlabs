from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_done: Optional[bool] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_done: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)