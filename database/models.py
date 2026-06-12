
from sqlalchemy import Boolean, Column, Integer, String
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    balance = Column(Integer, default=1000)
    is_admin = Column(Boolean, default=False)
    id_baned = Column(Boolean, default=False)
    
    
class game_history(Base):
    __tablename__="game_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    game = Column(String)
    balance = Column(Integer)
    time = Column(String)
    win = Column(Boolean)
    
    

