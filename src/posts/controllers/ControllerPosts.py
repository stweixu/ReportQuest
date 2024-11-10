import os
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from typing import Optional, List
from src.posts.models.PostModel import Post
from src.posts.services.PostService import PostService
from pydantic import BaseModel

router = APIRouter(prefix="/posts")


@router.post("/posts/", status_code=200)
async def create_post(
    user_id: str,
    title: Optional[str],
    description: Optional[str],
    image: Optional[UploadFile] = File(None),
    ):
    
    """Create a new post with authority and user information based on user_id."""

    # Define the image path based on the identifier and original extension
    file_extension = image.filename.split(".")[-1].lower()
    image_dir = "postImages"
    image_path = os.path.join(image_dir, f"{user_id}.{file_extension}")
    # Ensure the directory exists
    os.makedirs(image_dir, exist_ok=True)

    # Create an empty post with provided details
    post = Post.make_empty_post_with_details(
        title=title,
        description=description,
    )
    
    # Define the image path based on the identifier and original extension
    file_extension = image.filename.split(".")[-1].lower()
    image_path = os.path.join(image_dir, f"{post.post_id}.{file_extension}")

    # Save the image
    try:
        with open(image_path, "wb") as image_file:
            image_file.write(await image.read())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}",
        )
    
    post.image_path = image_path

    # Use PostService to create a post with authority info
    status_code, created_post = PostService.create_post_with_authority(user_id, post)
    if status_code == 201:
        return {"post_id": created_post.post_id, "title": created_post.title, "description": created_post.description, "image_path": created_post.image_path}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="User or authority not found")
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    """Retrieve a post by post_id."""
    status_code, post = PostService.read_entry(post_id)
    if status_code == 200:
        return post
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/posts/", response_model=List[Post])
def get_all_posts():
    """Retrieve all posts."""
    status_code, posts = PostService.read_all_entries()
    if status_code == 200:
        return posts
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

class PostUpdateRequest(BaseModel):
    title: Optional[str]
    description: Optional[str]
    image_path: Optional[str]
    authority_name: Optional[str]
    user_id: Optional[str]

@router.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: str, request: PostUpdateRequest):
    """Update an existing post."""
    status_code = PostService.update_entry(
        post_id=post_id,
        new_title=request.title,
        new_description=request.description,
        new_image_path=request.image_path,
        new_authority_name=request.authority_name,
        new_user_id=request.user_id
    )
    if status_code == 200:
        _, updated_post = PostService.read_entry(post_id)
        return updated_post
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: str):
    """Delete a post by post_id."""
    status_code = PostService.delete_entry(post_id)
    if status_code == 200:
        return
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        raise HTTPException(status_code=500, detail="Internal server error")
