import httpx
import pandas as pd
import ta
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.bybit_base = "https://api.bybit.com/v5"
        self.binance_base = "https://api.binance.com/api/v3"
        self.headers = {
            "X-API-Key": settings.BYBIT_API_KEY if settings.BYBIT_API_KEY else ""
        }

    async def fetch_klines(self, symbol: str, interval: str = "60", limit: int = 200) -> pd.DataFrame:
        """Fetches kline data from Bybit public endpoints (no secret required)"""
        url = f"{self.bybit_base}/market/kline"
        params = {
            "category": "linear",
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get('retCode') != 0:
                    raise ValueError(f"Bybit API Error: {data.get('retMsg')}")
                
                kline_data = data['result']['list']
                kline_data.reverse()  # Reverse to get chronological order
                
                df = pd.DataFrame(kline_data, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                ])
                
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                    
                df['open_time'] = pd.to_datetime(df['open_time'].astype(int), unit='ms')
                return df
                
            except Exception as e:
                logger.error(f"Error fetching klines for {symbol}: {e}")
                # Fallback to Binance if Bybit fails
                return await self._fetch_from_binance(symbol, interval, limit)

    async def _fetch_from_binance(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Fallback to Binance public API"""
        url = f"{self.binance_base}/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_vol', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
            
        df['open_time'] = pd.to_datetime(df['open_time'].astype(int), unit='ms')
        return df

    def calculate_indicators(self, df: pd.DataFrame) -> dict:
        """Calculates all technical indicators locally"""
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']

        indicators = {
            "current_price": float(close.iloc[-1]),
            "rsi": float(ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]),
            "macd": float(ta.trend.MACD(close).macd().iloc[-1]),
            "macd_signal": float(ta.trend.MACD(close).macd_signal().iloc[-1]),
            "ema_20": float(ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]),
            "ema_50": float(ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]),
            "ema_200": float(ta.trend.EMAIndicator(close, window=200).ema_indicator().iloc[-1]),
            "atr": float(ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1]),
            "bb_upper": float(ta.volatility.BollingerBands(close).bollinger_hband().iloc[-1]),
            "bb_lower": float(ta.volatility.BollingerBands(close).bollinger_lband().iloc[-1]),
            "vwap": float((volume * (high + low + close) / 3).cumsum() / volume.cumsum().iloc[-1]),
            "support": float(df['low'].rolling(window=20).min().iloc[-1]),
            "resistance": float(df['high'].rolling(window=20).max().iloc[-1]),
            "trend": self._determine_trend(close)
        }
        
        return indicators
    
    def _determine_trend(self, close: pd.Series) -> str:
        """Determine market trend"""
        ema_20 = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
        ema_50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]
        ema_200 = ta.trend.EMAIndicator(close, window=200).ema_indicator().iloc[-1]
        current_price = close.iloc[-1]
        
        if current_price > ema_20 > ema_50 > ema_200:
            return "STRONG_BULLISH"
        elif current_price > ema_20 > ema_50:
            return "BULLISH"
        elif current_price < ema_20 < ema_50 < ema_200:
            return "STRONG_BEARISH"
        elif current_price < ema_20 < ema_50:
            return "BEARISH"
        else:
            return "SIDEWAYS"
