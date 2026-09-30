from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.routes import router

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")