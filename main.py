from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slots import spin_reels, calculate_win as slots_calculate_win
from dice import calculate_win as dice_calculate_win
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    
    
    

        
        


