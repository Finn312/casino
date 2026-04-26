from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slots import spin_reels, calculate_win as slots_calculate_win
from dice import calculate_win as dice_calculate_win
from fastapi.middleware.cors import CORSMiddleware
from blackjack import shuffle_deck, hand_value, dealer_draw, check_winner

app = FastAPI()

game_state = {
    "deck": [],
    "player_hand": [],
    "dealer_hand": [],
    "bet": 0,
    "active": False
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
    
    return {
        "reels": reels,
        "win": win,
        "balance": new_balance
    }
    
    
    
    
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
    
    return {
        "win": win,
        "numbers": numbers,
        "balance": new_balance
    }
    
    
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
        "active": game_state["active"]
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
            "active": False
        }
    elif hand_value(game_state["player_hand"]) == 21:
        return {
            "player_hand": game_state["player_hand"],
            "player_value": 21,
            "result": "blackjack",
            "active": True
        }
    else:
        return {
            "player_hand": game_state["player_hand"],
            "player_value": hand_value(game_state["player_hand"]),
            "result": "continue",
            "active": True
        }


class BlackJackStandRequest(BaseModel):
    balance: int

@app.post("/blackjack/stand")
def blackjack_stand(request: BlackJackStandRequest):
    game_state["dealer_hand"] = dealer_draw(game_state["dealer_hand"], game_state["deck"])
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
        "balance": new_balance
    }