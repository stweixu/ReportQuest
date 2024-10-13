from fastapi import FastAPI
from src.users.ControllerUser import router as user_router
import uvicorn

app = FastAPI()


# adding more controllers follows this template
# from src.products.ControllerProduct import router as product_router
# app.include_router(product_router, prefix="/products", tags=["products"])

# Include the user router from the users directory
app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
