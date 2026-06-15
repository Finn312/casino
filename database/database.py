import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv


load_dotenv()

_BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_BASE_DIR}/data/casino.db")



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()