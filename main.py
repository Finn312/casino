from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine, Base
from routers import auth, games, admin, general


app = FastAPI()
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(admin.router)
app.include_router(general.router)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")



