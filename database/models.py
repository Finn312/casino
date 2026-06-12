
from sqlalchemy import Boolean, Column, Integer, String
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    balance = Column(Integer, default=1000)
    is_admin = Column(Boolean, default=False)
    
    
class game_history(Base):
    __tablename__="game_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    game = Column(String)
    balance = Column(Integer)
    time = Column(String)
    win = Column(Boolean)
    
    
from database.models import User

from database.database import SessionLocal

import bcrypt

db = SessionLocal()

hashed = bcrypt.hashpw("casino123".encode(), bcrypt.gensalt())

admin = User(username="admin", password=hashed.decode(), balance=9999, is_admin=True)

db.add(admin)

db.commit()

print("Admin erstellt!")