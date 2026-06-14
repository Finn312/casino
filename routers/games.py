from fastapi import APIRouter, Depends
from .gamelogic.slots import spin_reels, calculate_win as slots_calculate_win
from .gamelogic.blackjack import shuffle_deck, hand_value, dealer_draw, check_winner, game_state
from .gamelogic.dice import calculate_win as dice_calculate_win
from database.database import get_db
from database.models import User
import random
from core.schemas import SlotsRequest, BlackJackRequest, DiceRequest, ChickenGameRequest
from core.utilities import calculate_level

router = APIRouter()

#Slots Endpoint
@router.post("/spin")
def spin(request: SlotsRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}
    reels = spin_reels()
    win = slots_calculate_win(reels, request.bet)
    user.balance = user.balance - request.bet + win
    user.total_gold_earned += win
    db.commit()
    return {"reels": reels, "win": win, "new_balance": user.balance,"total_gold_earned": user.total_gold_earned, "level": calculate_level(user.total_gold_earned)}
  
  
#Blackjack Start Endpoint
@router.post("/blackjack/start")
def blackjack_start(request: BlackJackRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}

    game_state["deck"] = shuffle_deck()
    game_state["player_hand"] = [game_state["deck"].pop(0), game_state["deck"].pop(0)]
    game_state["dealer_hand"] = [game_state["deck"].pop(0), game_state["deck"].pop(0)]
    game_state["bet"] = request.bet
    game_state["active"] = True
    game_state["username"] = request.username

    if hand_value(game_state["player_hand"]) == 21:
        win = request.bet * 2
        user.balance = user.balance - request.bet + win
        user.total_gold_earned += win
        db.commit()
        return {
            "player_hand": game_state["player_hand"],
            "player_value": 21,
            "dealer_card": game_state["dealer_hand"][0],
            "active": False,
            "blackjack": True,
            "win": win,
            "new_balance": user.balance,
            "total_gold_earned": user.total_gold_earned,
            "level": calculate_level(user.total_gold_earned),
        }

    db.commit()
    return {
        "player_hand": game_state["player_hand"],
        "player_value": hand_value(game_state["player_hand"]),
        "dealer_card": game_state["dealer_hand"][0],
        "active": True,
        "total_gold_earned": user.total_gold_earned,
        "level": calculate_level(user.total_gold_earned),
    }
    
#Blackjack Hit Endpoint
@router.post("/blackjack/hit")
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


#Blackjack Stand Endpoint
@router.post("/blackjack/stand")
def blackjack_stand(db=Depends(get_db)):
    user = db.query(User).filter(User.username == game_state["username"]).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}

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

    user.balance = user.balance - game_state["bet"] + win
    user.total_gold_earned += win
    db.commit()
    game_state["active"] = False

    return {
        "player_hand": game_state["player_hand"],
        "player_value": player_value,
        "dealer_value": dealer_value,
        "dealer_hand": game_state["dealer_hand"],
        "gewinner": gewinner,
        "win": win,
        "new_balance": user.balance,
        "total_gold_earned": user.total_gold_earned, 
        "level": calculate_level(user.total_gold_earned)
    }
  

#Dice Endpoint
@router.post("/roll")
def roll(request: DiceRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}

    win, numbers = dice_calculate_win(request.bet, request.prediction, request.num_dice)
    user.balance = user.balance - request.bet + win
    user.total_gold_earned += win
    db.commit()

    return {"win": win, "numbers": numbers, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": calculate_level(user.total_gold_earned)}


#Chicken Game Endpoint
@router.post("/chicken_game")
def chicken_game(request: ChickenGameRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}
    if request.difficulty == 1:  # Easy
        survival = max(0.72, 0.82 - request.step * 0.008)
    else:  # Hard
        survival = max(0.55, 0.68 - request.step * 0.012)
    if random.random() < survival:
        result = "win"
    else:
        result = "lose"
        user.balance -= request.bet
    db.commit()
    return {"result": result, "win": 0, "new_balance": user.balance}
  
  
#ChickenGame cashout Endpoint
@router.post("/chicken_game_cashout")
def chicken_game_cashout(request: ChickenGameRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}

    win = request.bet * request.multiplier - request.bet
    user.balance += int(win)
    user.total_gold_earned += int(request.bet * request.multiplier)
    db.commit()

    return {"win": win, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": calculate_level(user.total_gold_earned)}
