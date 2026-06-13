from fastapi import APIRouter, Depends
from database.database import get_db
from database.models import User
import bcrypt
from core.schemas import LoginRequest
from core.utilities import calculate_level



router = APIRouter()


@router.post("/register")
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


@router.post("/login")
def login(request: LoginRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        return {"error": "Nutzer nicht gefunden"}
    if user.id_banned:
        return {"error": "Nutzer ist gebannt"}
    if not bcrypt.checkpw(request.password.encode(), user.password.encode()):
        return {"error": "Falsches Passwort"}

    return {
        "message": "Erfolgreich eingeloggt",
        "username": user.username,
        "balance": user.balance,
        "level": calculate_level(user.total_gold_earned),
        "total_gold_earned": user.total_gold_earned,
    }