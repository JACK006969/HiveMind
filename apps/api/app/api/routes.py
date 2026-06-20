from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import redis.asyncio as redis

from app.models.database import get_db, User, AISignal, PaperTrade, AuditLog
from app.services.market_data_service import MarketDataService
from app.services.research_engine import ResearchEngine
from app.services.risk_engine import RiskEngine
from app.core.config import settings

router = APIRouter()
market_service = MarketDataService()
research_engine = ResearchEngine()
risk_engine = RiskEngine()

# Redis for WebSocket pub/sub
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.get("/market/{symbol}/indicators")
async def get_market_indicators(symbol: str, interval: str = "60", limit: int = 200):
    """Get technical indicators for a symbol"""
    try:
        df = await market_service.fetch_klines(symbol, interval, limit)
        indicators = market_service.calculate_indicators(df)
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "indicators": indicators,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/analyze/{symbol}")
async def analyze_symbol(symbol: str, db: Session = Depends(get_db)):
    """Generate AI trading signal for a symbol"""
    try:
        # 1. Fetch market data
        df = await market_service.fetch_klines(symbol, "60", 200)
        technicals = market_service.calculate_indicators(df)
        
        # 2. Gather market context
        context = await research_engine.gather_market_context(symbol)
        
        # 3. Generate AI signal
        signal_data = await research_engine.generate_ai_signal(symbol, technicals, context)
        
        # 4. Save to database
        db_signal = AISignal(
            symbol=symbol.upper(),
            direction=signal_data["direction"],
            confidence_score=signal_data["confidence_score"],
            entry_zone=signal_data["entry_zone"],
            stop_loss=signal_data["stop_loss"],
            take_profit=signal_data["take_profit_targets"],
            risk_reward_ratio=signal_data["risk_reward_ratio"],
            reasoning=signal_data["reasoning"],
            market_outlook=signal_data["market_outlook"],
            technical_data=technicals,
            sentiment_data=context
        )
        db.add(db_signal)
        db.commit()
        db.refresh(db_signal)
        
        # 5. Publish to WebSocket
        await redis_client.publish("new_signals", json.dumps({
            "id": db_signal.id,
            "symbol": symbol.upper(),
            "direction": signal_data["direction"],
            "confidence_score": signal_data["confidence_score"],
            "timestamp": db_signal.created_at.isoformat()
        }))
        
        return signal_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/paper-trades")
async def create_paper_trade(
    trade_data: dict,
    db: Session = Depends(get_db)
):
    """Create a paper trade based on AI signal"""
    try:
        user_id = trade_data.get("user_id")
        signal_id = trade_data.get("signal_id")
        symbol = trade_data.get("symbol")
        direction = trade_data.get("direction")
        entry_price = float(trade_data.get("entry_price"))
        position_size = float(trade_data.get("position_size"))
        stop_loss = float(trade_data.get("stop_loss", 0))
        take_profit = float(trade_data.get("take_profit", 0))
        
        # Get user's risk profile
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate position sizing
        risk_calc = risk_engine.calculate_position_size(
            capital=float(user.total_paper_capital),
            risk_percentage=float(user.risk_profile),
            entry_price=entry_price,
            stop_loss_price=stop_loss
        )
        
        # Create paper trade
        paper_trade = PaperTrade(
            user_id=user_id,
            signal_id=signal_id,
            symbol=symbol.upper(),
            direction=direction,
            entry_price=entry_price,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="OPEN"
        )
        
        db.add(paper_trade)
        
        # Log audit
        audit = AuditLog(
            user_id=user_id,
            action="PAPER_TRADE_CREATED",
            metadata={"trade_id": paper_trade.id, "symbol": symbol}
        )
        db.add(audit)
        db.commit()
        db.refresh(paper_trade)
        
        return {
            "trade": paper_trade,
            "risk_calculation": risk_calc,
            "message": "Paper trade created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/paper-trades/{user_id}")
async def get_user_paper_trades(user_id: str, db: Session = Depends(get_db)):
    """Get all paper trades for a user"""
    trades = db.query(PaperTrade).filter(PaperTrade.user_id == user_id).order_by(PaperTrade.opened_at.desc()).all()
    return {"trades": trades, "count": len(trades)}

@router.get("/ai-signals/recent")
async def get_recent_signals(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent AI signals"""
    signals = db.query(AISignal).order_by(AISignal.created_at.desc()).limit(limit).all()
    return {"signals": signals, "count": len(signals)}

@router.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    """WebSocket endpoint for real-time signal updates"""
    await websocket.accept()
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("new_signals")
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                await websocket.send_json(json.loads(message["data"]))
    except WebSocketDisconnect:
        await redis_client.close()
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
