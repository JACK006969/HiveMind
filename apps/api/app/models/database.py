from sqlalchemy import create_engine, Column, String, DateTime, Numeric, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import settings
import uuid

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    avatar_url = Column(String)
    google_id = Column(String(255), unique=True)
    risk_profile = Column(Numeric(3, 2), default=0.02)  # 1%, 2%, or 3%
    total_paper_capital = Column(Numeric(15, 2), default=10000.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AISignal(Base):
    __tablename__ = "ai_signals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # LONG, SHORT, NO_TRADE
    confidence_score = Column(Numeric(5, 2), nullable=False)
    entry_zone = Column(JSON)
    stop_loss = Column(Numeric(15, 8))
    take_profit = Column(JSON)
    risk_reward_ratio = Column(Numeric(5, 2))
    reasoning = Column(String)
    market_outlook = Column(String)
    technical_data = Column(JSON)
    sentiment_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class PaperTrade(Base):
    __tablename__ = "paper_trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    signal_id = Column(String, nullable=True)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_price = Column(Numeric(15, 8), nullable=False)
    position_size = Column(Numeric(15, 8), nullable=False)
    stop_loss = Column(Numeric(15, 8))
    take_profit = Column(Numeric(15, 8))
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    pnl = Column(Numeric(15, 2), default=0.00)
    pnl_percentage = Column(Numeric(5, 2), default=0.00)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)
    action = Column(String(100), nullable=False)
    metadata = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Create tables
Base.metadata.create_all(bind=engine)
