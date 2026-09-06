from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class BaseEvent(BaseModel):
    event_id: str = Field(..., description="Unique idempotency key for the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"

class EmployeeRegisteredV1(BaseEvent):
    employee_id: str
    name: str
    department_id: str
    role: str
    joining_date: str

class AssessmentCompletedV1(BaseEvent):
    employee_id: str
    assessment_id: str
    skill_score: float
    weak_areas: List[str]
    strong_areas: List[str]

class PlanCreatedV1(BaseEvent):
    employee_id: str
    plan_id: str
    recommended_modules: List[str]

class TrainingAssignedV1(BaseEvent):
    employee_id: str
    module_id: str
    progress_id: str
    due_date: str

class TrainingCompletedV1(BaseEvent):
    employee_id: str
    module_id: str
    score: Optional[float] = None

class ProgressUpdatedV1(BaseEvent):
    employee_id: str
    module_id: str
    progress_id: str
    completion_status: str
    score: Optional[float] = None

class SupportQueryRaisedV1(BaseEvent):
    employee_id: str
    chat_id: str
    query_text: str
    resolved: bool

class ReportGeneratedV1(BaseEvent):
    report_id: str
    employee_id: Optional[str] = None
    report_type: str
    metrics: Dict[str, Any]
