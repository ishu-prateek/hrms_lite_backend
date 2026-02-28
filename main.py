from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routes.employees import router as employees_router
from src.routes.attendance import router as attendance_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HRMS Lite API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://hrms-lite-frontend-prateek.netlify.app"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employees_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to HRMS Lite API"}
