from pydantic import BaseModel

#Games
class SlotsRequest(BaseModel):
    bet: int
    username: str


class DiceRequest(BaseModel):
    bet: int
    username: str
    prediction: int
    num_dice: int = 2
    

class BlackJackRequest(BaseModel):
    bet: int
    username: str
    
    
class ChickenGameRequest(BaseModel):
  username: str
  bet: int
  step: int
  difficulty: int
  multiplier: float   


class BombGameRequest(BaseModel):
    username: str
    bet: int
    multiplier: float
    bombs: int
    revealed: int
    


#Auth
class LoginRequest(BaseModel):
    username: str
    password: str


#Admin
class AdminSetCreditsRequest(BaseModel):
    username: str
    password: str
    player_name: str
    new_balance: int


class AdminBanUserRequest(BaseModel):
    username: str
    password: str
    player_name: str
    


class UpdateBalanceRequest(BaseModel):
    username: str
    new_balance: int
    
    
class SaveHistoryRequest(BaseModel):
    username: str
    game: str
    balance: int
    win: bool
    time: str
    

class AskMurmelRequest(BaseModel):
    question: str


class UpdateSettingsRequest(BaseModel):
    username: str
    murmel_enabled: bool
    murmel_interval: int
    murmel_duration: int
    custom_input: bool
    

class DailyRequest(BaseModel):
    username: str
    

class RedeemCodeRequest(BaseModel):
    username: str
    code: str   
    

class AdminCreateCodeRequest(BaseModel):
    username: str
    password: str
    new_balance: int
    

