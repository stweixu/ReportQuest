from pydantic import BaseModel
from typing import Optional


class Report(BaseModel):
    user_id: str
    severity: int
    status: str
    report_id: str
    description: Optional[str]
    image_path: Optional[str]
    assigned_authority_uen: Optional[str]
    title: Optional[str]
    uen: Optional[str]
