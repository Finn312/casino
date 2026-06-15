from fastapi import APIRouter, Depends
from .gamelogic.slots import spin_reels, calculate_win as slots_calculate_win
from .gamelogic.blackjack import shuffle_deck, hand_value, dealer_draw, check_winner, game_states
from .gamelogic.dice import calculate_win as dice_calculate_win
from .gamelogic.bombs import calculate_multiplier
from database.database import get_db
from database.models import User
import random
from core.schemas import SlotsRequest, BlackJackRequest, BlackJackActionRequest, DiceRequest, ChickenGameRequest, BombGameRequest, RouletteRequest
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
    old_level = calculate_level(user.total_gold_earned)
    reels = spin_reels()
    win = slots_calculate_win(reels, request.bet)
    user.balance = user.balance - request.bet + win
    user.total_gold_earned += win
    new_level = calculate_level(user.total_gold_earned)
    if new_level > old_level:
        user.buzz_coins += new_level
    db.commit()
    return {"reels": reels, "win": win, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": new_level, "level_up": new_level > old_level, "buzz_coins": user.buzz_coins}
  
  
#Blackjack Start Endpoint
@router.post("/blackjack/start")
def blackjack_start(request: BlackJackRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}

    gs = {
        "deck": shuffle_deck(),
        "player_hand": [],
        "dealer_hand": [],
        "bet": request.bet,
        "active": True,
    }
    gs["player_hand"] = [gs["deck"].pop(0), gs["deck"].pop(0)]
    gs["dealer_hand"] = [gs["deck"].pop(0), gs["deck"].pop(0)]
    game_states[request.username] = gs

    old_level = calculate_level(user.total_gold_earned)
    if hand_value(gs["player_hand"]) == 21:
        win = request.bet * 2
        user.balance = user.balance - request.bet + win
        user.total_gold_earned += win
        new_level = calculate_level(user.total_gold_earned)
        if new_level > old_level:
            user.buzz_coins += new_level
        db.commit()
        del game_states[request.username]
        return {
            "player_hand": gs["player_hand"],
            "player_value": 21,
            "dealer_card": gs["dealer_hand"][0],
            "active": False,
            "blackjack": True,
            "win": win,
            "new_balance": user.balance,
            "total_gold_earned": user.total_gold_earned,
            "level": new_level,
            "level_up": new_level > old_level,
            "buzz_coins": user.buzz_coins,
        }

    db.commit()
    return {
        "player_hand": gs["player_hand"],
        "player_value": hand_value(gs["player_hand"]),
        "dealer_card": gs["dealer_hand"][0],
        "active": True,
        "total_gold_earned": user.total_gold_earned,
        "level": calculate_level(user.total_gold_earned),
    }

#Blackjack Hit Endpoint
@router.post("/blackjack/hit")
def blackjack_hit(request: BlackJackActionRequest, db=Depends(get_db)):
    gs = game_states.get(request.username)
    if not gs:
        return {"error": "Kein aktives Spiel"}
    gs["player_hand"].append(gs["deck"].pop(0))
    if hand_value(gs["player_hand"]) > 21:
        gs["active"] = False
        user = db.query(User).filter(User.username == request.username).first()
        if user:
            user.balance -= gs["bet"]
            db.commit()
            db.refresh(user)
        del game_states[request.username]
        return {
            "player_hand": gs["player_hand"],
            "player_value": hand_value(gs["player_hand"]),
            "result": "bust",
            "new_balance": user.balance if user else None,
            "active": False,
        }
    elif hand_value(gs["player_hand"]) == 21:
        return {
            "player_hand": gs["player_hand"],
            "player_value": 21,
            "result": "blackjack",
            "active": True,
        }
    else:
        return {
            "player_hand": gs["player_hand"],
            "player_value": hand_value(gs["player_hand"]),
            "result": "continue",
            "active": True,
        }


#Blackjack Stand Endpoint
@router.post("/blackjack/stand")
def blackjack_stand(request: BlackJackActionRequest, db=Depends(get_db)):
    gs = game_states.get(request.username)
    if not gs:
        return {"error": "Kein aktives Spiel"}
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}

    gs["dealer_hand"] = dealer_draw(gs["dealer_hand"], gs["deck"])
    player_value = hand_value(gs["player_hand"])
    dealer_value = hand_value(gs["dealer_hand"])
    gewinner = check_winner(player_value, dealer_value)

    if gewinner == "player":
        win = gs["bet"] * 2
    elif gewinner == "draw":
        win = gs["bet"]
    else:
        win = 0

    old_level = calculate_level(user.total_gold_earned)
    user.balance = user.balance - gs["bet"] + win
    user.total_gold_earned += win
    new_level = calculate_level(user.total_gold_earned)
    if new_level > old_level:
        user.buzz_coins += new_level
    db.commit()
    del game_states[request.username]

    return {
        "player_hand": gs["player_hand"],
        "player_value": player_value,
        "dealer_value": dealer_value,
        "dealer_hand": gs["dealer_hand"],
        "gewinner": gewinner,
        "win": win,
        "new_balance": user.balance,
        "total_gold_earned": user.total_gold_earned,
        "level": new_level,
        "level_up": new_level > old_level,
        "buzz_coins": user.buzz_coins,
    }
  

#Dice Endpoint
@router.post("/roll")
def roll(request: DiceRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}

    old_level = calculate_level(user.total_gold_earned)
    win, numbers = dice_calculate_win(request.bet, request.prediction, request.num_dice)
    user.balance = user.balance - request.bet + win
    user.total_gold_earned += win
    new_level = calculate_level(user.total_gold_earned)
    if new_level > old_level:
        user.buzz_coins += new_level
    db.commit()

    return {"win": win, "numbers": numbers, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": new_level, "level_up": new_level > old_level, "buzz_coins": user.buzz_coins}


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

    old_level = calculate_level(user.total_gold_earned)
    win = request.bet * request.multiplier - request.bet
    user.balance += int(win)
    user.total_gold_earned += int(request.bet * request.multiplier)
    new_level = calculate_level(user.total_gold_earned)
    if new_level > old_level:
        user.buzz_coins += new_level
    db.commit()

    return {"win": win, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": new_level, "level_up": new_level > old_level, "buzz_coins": user.buzz_coins}



@router.post("/mines_game")
def mines_game(request: BombGameRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}
    safe_tiles = 25 - request.bombs - request.revealed
    remaining_tiles = 25 - request.revealed
    chance_safe = safe_tiles / remaining_tiles
    if random.random() < chance_safe:
        result = "win"
        new_multiplier = calculate_multiplier(request.bombs, request.revealed + 1)
    else:
        result = "lose"
        user.balance -= request.bet
        db.commit()
    return {"result": result, "new_balance": user.balance, "multiplier": new_multiplier if result == "win" else 0}


@router.post("/mines_game_cashout")
def mines_game_cashout(request: BombGameRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}

    old_level = calculate_level(user.total_gold_earned)
    win = request.bet * request.multiplier - request.bet
    user.balance += int(win)
    user.total_gold_earned += int(request.bet * request.multiplier)
    new_level = calculate_level(user.total_gold_earned)
    if new_level > old_level:
        user.buzz_coins += new_level
    db.commit()

    return {"win": win, "new_balance": user.balance, "total_gold_earned": user.total_gold_earned, "level": new_level, "level_up": new_level > old_level, "buzz_coins": user.buzz_coins}



RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

@router.post("/roulette_game")
def roulette_game(request: RouletteRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if request.bet > user.balance:
        return {"error": "Not enough credits"}

    spin = random.randint(0, 36)

    if request.bet_type == "red":
        won = spin in RED_NUMBERS
    elif request.bet_type == "black":
        won = spin not in RED_NUMBERS and spin != 0
    elif request.bet_type == "even":
        won = spin != 0 and spin % 2 == 0
    elif request.bet_type == "odd":
        won = spin % 2 == 1
    elif request.bet_type == "1-12":
        won = 1 <= spin <= 12
    elif request.bet_type == "13-24":
        won = 13 <= spin <= 24
    elif request.bet_type == "25-36":
        won = 25 <= spin <= 36
    elif request.bet_type == "number":
        won = spin == request.bet_value
    else:
        return {"error": "Ungültiger Wetttyp"}

    old_level = calculate_level(user.total_gold_earned)
    level_up = False
    if won:
        multiplier = 36 if request.bet_type == "number" else (3 if request.bet_type in ["1-12", "13-24", "25-36"] else 2)
        winnings = request.bet * multiplier - request.bet
        user.balance += int(winnings)
        user.total_gold_earned += int(request.bet * multiplier)
        new_level = calculate_level(user.total_gold_earned)
        if new_level > old_level:
            user.buzz_coins += new_level
            level_up = True
    else:
        winnings = -request.bet
        user.balance -= request.bet
        new_level = old_level

    db.commit()

    return {
        "spin": spin,
        "won": won,
        "winnings": winnings,
        "new_balance": user.balance,
        "level": new_level,
        "level_up": level_up,
        "buzz_coins": user.buzz_coins,
    }