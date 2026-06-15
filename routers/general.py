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


TIER_COIN_PACKAGES = [
    {1: 5_000,  3: 16_000,  5:  28_000, 10:  60_000},  # lv  1-10
    {1: 10_000, 3: 32_000,  5:  56_000, 10: 120_000},  # lv 11-20
    {1: 18_000, 3: 57_000,  5: 100_000, 10: 210_000},  # lv 21-30
    {1: 28_000, 3: 88_000,  5: 155_000, 10: 325_000},  # lv 31-40
    {1: 40_000, 3: 125_000, 5: 220_000, 10: 460_000},  # lv 41-50
]

WHEEL_BREAKPOINTS = [
    [50,  500,  5_000,  25_000,  100_000,   300_000,   500_000],  # lv  1-10
    [100, 900,  9_000,  45_000,  180_000,   540_000,   900_000],  # lv 11-20
    [180, 1_600, 16_000, 80_000,  320_000,   960_000, 1_600_000],  # lv 21-30
    [300, 2_800, 28_000, 140_000, 560_000, 1_680_000, 2_800_000],  # lv 31-40
    [500, 5_000, 50_000, 250_000, 1_000_000, 3_000_000, 5_000_000],  # lv 41-50
]


def _get_tier(level: int) -> int:
    if level <= 10: return 0
    if level <= 20: return 1
    if level <= 30: return 2
    if level <= 40: return 3
    return 4


@router.post("/shop/buy_coins")
def shop_buy_coins(request: BuyCoinsRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    tier = _get_tier(calculate_level(user.total_gold_earned))
    packages = TIER_COIN_PACKAGES[tier]
    if request.package not in packages:
        return {"error": "Ungültiges Paket"}
    if user.buzz_coins < request.package:
        return {"error": f"Nicht genug Buzz Coins (benötigt: {request.package})"}
    coins = packages[request.package]
    user.buzz_coins -= request.package
    user.balance += coins
    db.commit()
    return {"new_balance": user.balance, "buzz_coins": user.buzz_coins, "coins_received": coins}


def _wheel_reward(level: int) -> int:
    bp = WHEEL_BREAKPOINTS[_get_tier(level)]
    r = random.random()
    if r < 0.18:
        return random.randint(bp[0], bp[1])
    elif r < 0.40:
        return random.randint(bp[1], bp[2])
    elif r < 0.55:
        return random.randint(bp[2], bp[3])
    elif r < 0.85:
        return random.randint(bp[3], bp[4])
    elif r < 0.96:
        return random.randint(bp[4], bp[5])
    else:
        return random.randint(bp[5], bp[6])


@router.post("/shop/spin_wheel")
def shop_spin_wheel(request: SpinWheelRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if user.buzz_coins < 5:
        return {"error": "Nicht genug Buzz Coins (benötigt: 5)"}
    level = calculate_level(user.total_gold_earned)
    reward = _wheel_reward(level)
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