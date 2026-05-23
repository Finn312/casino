from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import Boolean
from slots import spin_reels, calculate_win as slots_calculate_win
from dice import calculate_win as dice_calculate_win
from fastapi.middleware.cors import CORSMiddleware
from blackjack import shuffle_deck, hand_value, dealer_draw, check_winner
from database.database import engine, Base, get_db
from database import models
from database.models import User, game_history
import bcrypt

app = FastAPI()

Base.metadata.create_all(bind=engine)

game_state = {
    "deck": [],
    "player_hand": [],
    "dealer_hand": [],
    "bet": 0,
    "active": False,
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class SpinRequest(BaseModel):
    bet: int
    balance: int


@app.post("/spin")
def spin(request: SpinRequest):
    if request.bet > request.balance:
        return {"error": "Not enough credits"}

    reels = spin_reels()
    win = slots_calculate_win(reels, request.bet)
    new_balance = request.balance - request.bet + win

    return {"reels": reels, "win": win, "balance": new_balance}


class RollRequest(BaseModel):
    bet: int
    balance: int
    prediction: int
    num_dice: int = 2


@app.post("/roll")
def roll(request: RollRequest):
    if request.bet > request.balance:
        return {"error": "Not enough credits"}

    win, numbers = dice_calculate_win(request.bet, request.prediction, request.num_dice)
    new_balance = request.balance - request.bet + win

    return {"win": win, "numbers": numbers, "balance": new_balance}


class BlackJackRequest(BaseModel):
    bet: int
    balance: int


@app.post("/blackjack/start")
def blackjack_start(request: BlackJackRequest):
    if request.bet > request.balance:
        return {"error": "Not enough credits"}

    game_state["deck"] = shuffle_deck()
    game_state["player_hand"] = [game_state["deck"].pop(0), game_state["deck"].pop(0)]
    game_state["dealer_hand"] = [game_state["deck"].pop(0), game_state["deck"].pop(0)]
    game_state["bet"] = request.bet
    game_state["active"] = True

    return {
        "player_hand": game_state["player_hand"],
        "player_value": hand_value(game_state["player_hand"]),
        "dealer_card": game_state["dealer_hand"][0],
        "active": game_state["active"],
    }


@app.post("/blackjack/hit")
def blackjack_hit():
    game_state["player_hand"].append(game_state["deck"].pop(0))
    if hand_value(game_state["player_hand"]) > 21:
        game_state["active"] = False
        return {
            "player_hand": game_state["player_hand"],
            "player_value": hand_value(game_state["player_hand"]),
            "result": "bust",
            "active": False,
        }
    elif hand_value(game_state["player_hand"]) == 21:
        return {
            "player_hand": game_state["player_hand"],
            "player_value": 21,
            "result": "blackjack",
            "active": True,
        }
    else:
        return {
            "player_hand": game_state["player_hand"],
            "player_value": hand_value(game_state["player_hand"]),
            "result": "continue",
            "active": True,
        }


class BlackJackStandRequest(BaseModel):
    balance: int


@app.post("/blackjack/stand")
def blackjack_stand(request: BlackJackStandRequest):
    game_state["dealer_hand"] = dealer_draw(
        game_state["dealer_hand"], game_state["deck"]
    )
    player_value = hand_value(game_state["player_hand"])
    dealer_value = hand_value(game_state["dealer_hand"])
    gewinner = check_winner(player_value, dealer_value)

    if gewinner == "player":
        win = game_state["bet"] * 2
    elif gewinner == "draw":
        win = game_state["bet"]
    else:
        win = 0

    new_balance = request.balance - game_state["bet"] + win
    game_state["active"] = False

    return {
        "player_hand": game_state["player_hand"],
        "player_value": player_value,
        "dealer_value": dealer_value,
        "dealer_hand": game_state["dealer_hand"],
        "gewinner": gewinner,
        "balance": new_balance,
    }


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(request: LoginRequest, db=Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        return {"error": "Es gitb diesen Namen bereits"}
    else:
        hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())
        new_user = User(username=request.username, password=hashed_password.decode())
        db.add(new_user)
        db.commit()
        return {
            "message": "Erfolgreich registriert",
            "username": new_user.username,
            "balance": new_user.balance,
        }


@app.post("/login")
def login(request: LoginRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if not bcrypt.checkpw(request.password.encode(), user.password.encode()):
        return {"error": "Falsches Passwort"}

    return {
        "message": "Erfolgreich eingeloggt",
        "username": user.username,
        "balance": user.balance,
    }


class UpdateBalanceRequest(BaseModel):
    username: str
    new_balance: int


@app.post("/update_balance")
def update_balance(request: UpdateBalanceRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}

    user.balance = request.new_balance
    db.commit()

    return {"message": "Balance aktualisiert", "new_balance": user.balance}


@app.get("/leaderboard")
def leaderboard(db=Depends(get_db)):
    users = db.query(User).order_by(User.balance.desc()).all()
    return [{"username": u.username, "balance": u.balance} for u in users]


class SaveHistoryRequest(BaseModel):
    username: str
    game: str
    balance: int
    win: bool
    time: str
    
    
@app.post("/SaveHistory")
def save_history(request: SaveHistoryRequest,db=Depends(get_db)):
    new_history = game_history(username=request.username, game=request.game,balance=request.balance,win=request.win,time=request.time)
    db.add(new_history)
    db.commit()
    return{
        "message": "Saved",
        "username": new_history.username,
        "game": new_history.game,
        "balance": new_history.balance,
        "win": new_history.win,
        "time": new_history.time
    }
    
    
@app.get("/get_history")
def GetHistory(username: str, db=Depends(get_db)):
    history = db.query(game_history).filter(game_history.username == username).all()
    return [{"username":h.username,"game":h.game,"balance":h.balance,"win":h.win,"time":h.time}for h in history]
    