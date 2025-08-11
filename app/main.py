from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import file_uploder
import os

print("main.py loaded")

app = FastAPI()

app.include_router(file_uploder.router)

# base_dir = os.path.dirname(os.path.dirname(__file__))
# frontend_dir = os.path.join(base_dir, "frontend")

# app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# # Serve the frontend folder
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")