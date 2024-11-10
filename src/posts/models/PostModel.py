from pydantic import BaseModel
from typing import Optional


class Post(BaseModel):
    post_id: str
    description: Optional[str]
    image_path: Optional[str]
    authority_name: str
