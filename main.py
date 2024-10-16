from fastapi import FastAPI, Depends, HTTPException, status
from src.users.controllers.ControllerUser import router as user_router
from src.users.controllers.ControllerPublic import router as public_router
from src.reports.controllers.ControllerReports import router as reports_router
import uvicorn

app = FastAPI()


# adding more controllers follows this template
# from src.products.ControllerProduct import router as product_router
# app.include_router(product_router, prefix="/products", tags=["products"])


# Include the user router from the users directory
app.include_router(public_router, prefix="/public", tags=["public"])

app.include_router(user_router, prefix="/users", tags=["users"])

app.include_router(reports_router, prefix="/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
