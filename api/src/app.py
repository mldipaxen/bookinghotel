from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from config import AUTH_SECRET
from src.pages.router import page_router
from src.v1.api import api_router
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=AUTH_SECRET)

app.mount("/pages/static", StaticFiles(directory="src/static"), name="static")

app.include_router(api_router, prefix="/api/v1")
app.include_router(page_router, prefix="/pages")


@app.get("/")
async def index():
    return RedirectResponse(url="/pages/login")


@app.get("/pages")
async def index():
    return RedirectResponse(url="/pages/login")
