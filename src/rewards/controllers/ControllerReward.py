from fastapi import APIRouter, HTTPException, status
from typing import Optional
import uuid
from datetime import datetime, timedelta

from src.rewards.models.RewardModel import Reward, RewardCreate, RewardRead
from src.rewards.services.RewardService import RewardService

router = APIRouter(prefix="/rewards")

# Instantiate RewardService (assuming it manages connection and interaction with the database)
reward_service = RewardService()

@router.get("/all", response_model=list[RewardRead])
async def read_all_rewards():
    """Retrieve all rewards."""
    status_code, rewards = reward_service.read_all_rewards()
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail="Failed to retrieve rewards.")
    return rewards

@router.get("/{reward_id}", response_model=Optional[RewardRead])
async def read_reward_by_id(reward_id: str):
    """Retrieve a reward by its ID."""
    status_code, reward = reward_service.read_reward_by_id(reward_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reward.")
    return reward

@router.post("/", response_model=RewardRead)
async def create_reward(reward: RewardCreate):
    """Create a new reward."""
    new_reward = Reward(
        rewardID=str(uuid.uuid4()),
        description=reward.description,
        pointsRequired=reward.pointsRequired,
        validity=reward.validity,
        availability=reward.availability,
        userID=reward.userID
    )
    status_code, created_reward = reward_service.create_reward(new_reward)
    if status_code == 201:
        return created_reward
    elif status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create reward.")
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create reward.")

@router.put("/{reward_id}/quantity", response_model=dict)
async def update_reward_quantity(reward_id: str, quantity: int):
    """Update reward quantity."""
    status_code = reward_service.update_reward_quantity(reward_id, quantity)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update reward quantity.")
    return {"detail": "Reward quantity updated successfully."}

@router.get("/{reward_id}/validity", response_model=dict)
async def check_reward_validity(reward_id: str):
    """Check the validity of a reward."""
    status_code, reward = reward_service.read_reward_by_id(reward_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reward.")
    
    is_valid = reward.getValidity()
    return {"is_valid": is_valid}

@router.post("/{reward_id}/generate", response_model=dict)
async def generate_encoded_reward(reward_id: str, duration: int):
    """Generate a Base64-encoded reward string with specified duration."""
    status_code, reward = reward_service.read_reward_by_id(reward_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reward.")
    
    encoded_reward = reward.generateReward(duration)
    return {"encoded_reward": encoded_reward}

@router.post("/decode", response_model=dict)
async def decode_reward(encoded_recipe: str):
    """Decode a Base64-encoded reward string."""
    reward = Reward(rewardID="dummy", description="dummy", pointsRequired=0, validity=0, availability=0)
    decoded_reward = reward.decodeReward(encoded_recipe)
    return {"decoded_reward": decoded_reward}

@router.delete("/{reward_id}", response_model=dict)
async def delete_reward(reward_id: str):
    """Delete a reward by its ID."""
    status_code = reward_service.delete_reward_by_id(reward_id)
    if status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
    elif status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete reward.")
    return {"detail": "Reward deleted successfully."}

@router.delete("/wipe", response_model=dict)
async def wipe_rewards():
    """Wipe all rewards from the database."""
    status_code = reward_service.wipe_all_rewards()
    if status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to wipe rewards.")
    return {"detail": "All rewards wiped successfully."}
