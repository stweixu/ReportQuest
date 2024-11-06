from typing import Optional
from pydantic import BaseModel, Field


class MyRewards(BaseModel):
    reward_id: str = Field(..., alias="rewardId")
    user_id: str = Field(..., alias="userId")
    expiry: int
    giftcode: Optional[str]
