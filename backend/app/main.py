from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, lessons, leveling, practice

app = FastAPI(title="Daily10 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(leveling.router)
app.include_router(lessons.router)
app.include_router(practice.router)


@app.get("/health")
def health():
    return {"status": "ok"}
