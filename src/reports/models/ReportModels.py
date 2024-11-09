from pydantic import BaseModel
from typing import Optional


class Report(BaseModel):
    user_id: str
    relevance: int
    severity: int
    urgency: int
    status: str = "Pending"
    #change the migration script please :)
    report_id: str
    description: Optional[str]
    image_path: Optional[str]
    title: Optional[str]
    datetime: int
    location: str  # Ensure this is included if required
