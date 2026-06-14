from fastapi import APIRouter, Depends
from database.database import get_db
from database.models import User, game_history, Settings
from core.schemas import UpdateBalanceRequest, SaveHistoryRequest, AskMurmelRequest, UpdateSettingsRequest
from database import models
import requests
from core.utilities import calculate_level
from dotenv import load_dotenv
import os


load_dotenv("/Users/finn/Desktop/Casino/.env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
router = APIRouter()


#Leaderboard Endpoint
@router.get("/leaderboard")
def leaderboard(db=Depends(get_db)):
    leaderboard_users = (
        db.query(User)
        .filter(
            User.show_in_leaderboard == True,
            User.id_banned == False,
            User.is_admin == False,
        )
        .order_by(User.balance.desc())
        .limit(10)
        .all()
    )
    return [{"username": u.username, "balance": u.balance} for u in leaderboard_users]
  

#Update Balance Endpoint
@router.post("/update_balance")
def update_balance(request: UpdateBalanceRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    user.balance = request.new_balance
    db.commit()
    return {"message": "Balance aktualisiert", "new_balance": user.balance}



#Save History Endpoint
@router.post("/SaveHistory")
def save_history(request: SaveHistoryRequest, db=Depends(get_db)):
    new_history = game_history(
        username=request.username,
        game=request.game,
        balance=request.balance,
        win=request.win,
        time=request.time,
    )
    db.add(new_history)
    db.commit()
    return {
        "message": "Saved",
        "username": new_history.username,
        "game": new_history.game,
        "balance": new_history.balance,
        "win": new_history.win,
        "time": new_history.time,
    }
    

#Get History Endpoint
@router.get("/get_history")
def GetHistory(username: str, db=Depends(get_db)):
    history = db.query(game_history).filter(game_history.username == username).all()
    return [
        {
            "username": h.username,
            "game": h.game,
            "balance": h.balance,
            "win": h.win,
            "time": h.time,
        }
        for h in history
    ]



#Get Balance Endpoint
@router.get("/get_balance")
def get_balance(username: str, db=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    return {
        "balance": user.balance,
        "id_banned": user.id_banned,
        "total_gold_earned": user.total_gold_earned,
        "level": calculate_level(user.total_gold_earned),
    }



#Ask Murmel Endpoint
@router.post("/ask_murmel")
def ask_murmel(request: AskMurmelRequest):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "Du bist Murmel, ein freches witziges Murmeltier im Smoking das in einem Online-Casino arbeitet. Du erklärst Spiele, gibst Tipps und machst Witze. Antworte kurz und auf Deutsch.",
                },
                {"role": "user", "content": request.question},
            ],
        },
    )
    data = response.json()
    print(data)
    return {"answer": data["choices"][0]["message"]["content"]}



#Get Settings Endpoint
@router.get("/get_settings")
def get_settings(username: str, db=Depends(get_db)):
    settings = db.query(models.Settings).filter(models.Settings.username == username).first()
    if not settings:
        return {"error": "Settings not found"}
    return {
        "murmel_enabled": settings.murmel_enabled,
        "murmel_interval": settings.murmel_interval,
        "murmel_duration": settings.murmel_duration,
    }


#Update Settings Endpoint
@router.post("/update_settings")
def update_settings(request: UpdateSettingsRequest, db=Depends(get_db)):
    settings = db.query(models.Settings).filter(models.Settings.username == request.username).first()
    if not settings:
        settings = models.Settings(
            username=request.username,
            murmel_enabled=request.murmel_enabled,
            murmel_interval=request.murmel_interval,
            murmel_duration=request.murmel_duration,
        )
        db.add(settings)
    else:
        settings.murmel_enabled = request.murmel_enabled
        settings.murmel_interval = request.murmel_interval
        settings.murmel_duration = request.murmel_duration
    db.commit()
    return {"message": "Settings updated"}