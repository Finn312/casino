from fastapi import APIRouter, Depends
from database.database import get_db
from database.models import User, game_history, Settings, coin_codes
from core.schemas import UpdateBalanceRequest, SaveHistoryRequest, AskMurmelRequest, UpdateSettingsRequest, DailyRequest, RedeemCodeRequest, BuyCoinsRequest, SpinWheelRequest
from database import models
import requests
from core.utilities import calculate_level
from dotenv import load_dotenv
import os
from datetime import datetime
import random

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
            User.total_gold_earned >= 2000,
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
        "buzz_coins": user.buzz_coins,
        "is_admin": user.is_admin,
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
        "custom_input": settings.custom_input,
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
            custom_input=request.custom_input,
        )
        db.add(settings)
    else:
        settings.murmel_enabled = request.murmel_enabled
        settings.murmel_interval = request.murmel_interval
        settings.murmel_duration = request.murmel_duration
        settings.custom_input = request.custom_input
    db.commit()
    return {"message": "Settings updated"}



@router.post("/daily_spin")
def daily_spin(request: DailyRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if user.last_dayle and (datetime.utcnow() - user.last_dayle).total_seconds() < 24 * 3600:
        return {"error": "Du kannst nur einmal alle 24 Stunden drehen"}
    level = calculate_level(user.total_gold_earned)
    base = 500 + (level * 500)
    reward = random.randint(base, base * 3)
    user.balance += reward
    user.last_dayle = datetime.utcnow()
    db.commit()
    return {"message": f"Du hast {reward} Gold gewonnen!", "new_balance": user.balance, "reward": reward}



@router.get("/get_dayle_status")
def get_dayle_status(username: str, db=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if user.last_dayle and (datetime.utcnow() - user.last_dayle).total_seconds() < 24 * 3600:
        remaining_time = 24 * 3600 - (datetime.utcnow() - user.last_dayle).total_seconds()
        return {"can_spin": False, "remaining_time": remaining_time}
    return {"can_spin": True, "remaining_time": 0}


COIN_PACKAGES = {
    1:  5_000,
    3:  16_000,
    5:  28_000,
    10: 60_000,
}

@router.post("/shop/buy_coins")
def shop_buy_coins(request: BuyCoinsRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.package not in COIN_PACKAGES:
        return {"error": "Ungültiges Paket"}
    if user.buzz_coins < request.package:
        return {"error": f"Nicht genug Buzz Coins (benötigt: {request.package})"}
    coins = COIN_PACKAGES[request.package]
    user.buzz_coins -= request.package
    user.balance += coins
    db.commit()
    return {"new_balance": user.balance, "buzz_coins": user.buzz_coins}


def _wheel_reward() -> int:
    r = random.random()
    if r < 0.18:        # 18 %
        return random.randint(55, 550)
    elif r < 0.40:      # 22 %
        return random.randint(550, 5_500)
    elif r < 0.55:      # 15 %
        return random.randint(5_500, 27_500)
    elif r < 0.85:      # 30 %
        return random.randint(27_500, 110_000)
    elif r < 0.96:      # 11 %
        return random.randint(110_000, 330_000)
    else:               #  4 %
        return random.randint(330_000, 550_000)


@router.post("/shop/spin_wheel")
def shop_spin_wheel(request: SpinWheelRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if user.buzz_coins < 5:
        return {"error": "Nicht genug Buzz Coins (benötigt: 5)"}
    reward = _wheel_reward()
    user.buzz_coins -= 5
    user.balance += reward
    db.commit()
    return {"reward": reward, "new_balance": user.balance, "buzz_coins": user.buzz_coins}


@router.post("/redeem_code")
def redeem_code(request: RedeemCodeRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    code_entry = db.query(coin_codes).filter(coin_codes.code == request.code).first()
    if not code_entry:
        return {"error": "Ungültiger Code"}
    user.balance += code_entry.value
    db.delete(code_entry)
    db.commit()
    return {"message": f"Code eingelöst! Du hast {code_entry.value} Gold erhalten.", "new_balance": user.balance}