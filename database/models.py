
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    balance = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    id_banned = Column(Boolean, default=False)
    show_in_leaderboard = Column(Boolean, default=True)
    total_gold_earned = Column(Integer, default=0)
    last_dayle = Column(DateTime)
    buzz_coins = Column(Integer, default=0)
    
class game_history(Base):
    __tablename__="game_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    game = Column(String)
    balance = Column(Integer)
    time = Column(String)
    win = Column(Boolean)
    
    
class Settings(Base):
    __tablename__="Settings"
    
    username = Column(String, primary_key=True, index=True)
    murmel_enabled = Column(Boolean, default=True)
    murmel_interval = Column(Integer, default=60)
    murmel_duration = Column(Integer, default=5)    
    custom_input = Column(Boolean, default=False)
    

class coin_codes(Base):
    __tablename__="coin_codes"
    
    code = Column(String, primary_key=True, index=True)
    value = Column(Integer)