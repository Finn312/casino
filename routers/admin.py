from fastapi import APIRouter, Depends
from database.database import get_db
from database.models import User, game_history
from database import models
import bcrypt
import secrets
from core.schemas import AdminBanUserRequest, AdminSetCreditsRequest, AdminCreateCodeRequest, AdminSetLevelRequest, AdminSetBuzzCoinsRequest

router = APIRouter()


#Admin chance Credits Endpoint
@router.post("/admin/set_credits")
def admin_set_credits(request: AdminSetCreditsRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    player.balance = request.new_balance
    db.commit()

    return {
        "message": "Balance updated",
        "player_name": player.username,
        "new_balance": player.balance,
    }



#Admin Set Level Endpoint
@router.post("/admin/set_level")
def admin_set_level(request: AdminSetLevelRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    if request.level < 0 or request.level > 50:
        return {"error": "Level muss zwischen 0 und 50 liegen"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    from core.utilities import LEVEL_THRESHOLDS
    player.total_gold_earned = LEVEL_THRESHOLDS[request.level]
    db.commit()

    return {
        "message": "Level updated",
        "player_name": player.username,
        "new_level": request.level,
        "total_gold_earned": player.total_gold_earned,
    }


#Admin Ban User Endpoint
@router.post("/admin/ban_user")
def admin_ban_user(request: AdminBanUserRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    player.id_banned = True
    db.commit()

    return {
        "message": "User banned",
        "player_name": player.username,
    }
    
    

#Admin Unban User Endpoint
@router.post("/admin/unban_user")
def admin_unban_user(request: AdminBanUserRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    player.id_banned = False
    db.commit()

    return {
        "message": "User unbanned",
        "player_name": player.username,
    }


#Admin Delete User Endpoint
@router.post("/admin/delete_user")
def admin_delete_user(request: AdminBanUserRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    db.delete(player)
    db.commit()

    return {
        "message": "User deleted",
        "player_name": request.player_name,
    }
    
    
#Admin Get User Endpoint
@router.get("/admin/get_users")
def admin_get_users(username: str, password: str, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    from core.utilities import calculate_level
    users = db.query(User).all()
    return [
        {
            "username": u.username,
            "balance": u.balance,
            "is_admin": u.is_admin,
            "id_banned": u.id_banned,
            "show_in_leaderboard": u.show_in_leaderboard,
            "level": calculate_level(u.total_gold_earned or 0),
        }
        for u in users
    ]


#Admin Get History Endpoint
@router.get("/admin/get_history")
def admin_get_history(username: str, password: str, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    history = db.query(game_history).order_by(game_history.id.desc()).limit(50).all()
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
    


#Show in leaderboard Endpoint
@router.post("/show_in_leaderboard")
def show_in_leaderboard(request: AdminBanUserRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    player.show_in_leaderboard = not player.show_in_leaderboard
    db.commit()

    return {
        "message": "Leaderboard visibility toggled",
        "player_name": player.username,
        "show_in_leaderboard": player.show_in_leaderboard,
    }



@router.post("/admin/set_buzz_coins")
def admin_set_buzz_coins(request: AdminSetBuzzCoinsRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    player = db.query(User).filter(User.username == request.player_name).first()
    if not player:
        return {"error": "Player not found"}

    player.buzz_coins = request.amount
    db.commit()

    return {"username": player.username, "buzz_coins": player.buzz_coins}


@router.post("/admin/create_coin_code")
def create_coin_code(request: AdminCreateCodeRequest, db=Depends(get_db)):
    admin_user = db.query(User).filter(User.username == request.username).first()
    if not admin_user or not admin_user.is_admin:
        return {"error": "Unauthorized"}
    if not bcrypt.checkpw(request.password.encode(), admin_user.password.encode()):
        return {"error": "Falsches Passwort"}

    code = secrets.token_hex(4).upper()
    while db.query(models.coin_codes).filter(models.coin_codes.code == code).first():
        code = secrets.token_hex(4).upper()

    new_code = models.coin_codes(code=code, value=request.new_balance)
    db.add(new_code)
    db.commit()

    return {
        "message": "Coin code created",
        "code": new_code.code,
        "value": new_code.value,
    }