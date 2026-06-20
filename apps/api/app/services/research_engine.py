import httpx
from groq import AsyncGroq
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class ResearchEngine:
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.fear_greed_url = "https://api.alternative.me/fng/?limit=7"

    async def gather_market_context(self, symbol: str) -> dict:
        """Gathers Fear & Greed, Funding Rates, and Open Interest from public APIs"""
        context = {
            "fear_greed_index": 50,
            "fear_greed_classification": "Neutral",
            "funding_rate": 0.0001,
            "open_interest": 0,
            "social_sentiment": "Neutral"
        }
        
        try:
            # 1. Fear and Greed Index
            async with httpx.AsyncClient() as client:
                fg_response = await client.get(self.fear_greed_url, timeout=5.0)
                if fg_response.status_code == 200:
                    fg_data = fg_response.json()
                    if fg_data.get('status') == 'success' and fg_data.get('data'):
                        latest = fg_data['data'][0]
                        context["fear_greed_index"] = int(latest['value'])
                        context["fear_greed_classification"] = latest['value_classification']
                        
                        # Calculate trend (7-day average)
                        if len(fg_data['data']) > 1:
                            avg_7d = sum(int(d['value']) for d in fg_data['data']) / len(fg_data['data'])
                            context["fear_greed_trend"] = "Improving" if latest['value'] > avg_7d else "Worsening"
                
                # 2. Bybit Funding Rate & Open Interest (Public endpoint)
                bybit_url = f"https://api.bybit.com/v5/markets/tickers"
                params = {"category": "linear", "symbol": symbol.upper()}
                bybit_response = await client.get(bybit_url, params=params, timeout=5.0)
                
                if bybit_response.status_code == 200:
                    bybit_data = bybit_response.json()
                    if bybit_data.get('retCode') == 0 and bybit_data['result']['list']:
                        ticker = bybit_data['result']['list'][0]
                        context["funding_rate"] = float(ticker.get('fundingRate', 0))
                        context["open_interest"] = float(ticker.get('openInterest', 0))
                        context["24h_volume"] = float(ticker.get('volume24h', 0))
                        
        except Exception as e:
            logger.error(f"Error gathering market context: {e}")
            # Return default context on error
        
        return context

    async def generate_ai_signal(self, symbol: str, technicals: dict, context: dict) -> dict:
        """Sends structured data to Groq for AI analysis"""
        
        system_prompt = """You are HiveMind, an elite quantitative crypto trading AI copilot.
Analyze the provided technical indicators and market context to generate a trading signal.

CRITICAL RULES:
1. This is a COPILOT tool - NEVER suggest automated execution
2. Always include risk warnings
3. Be conservative with confidence scores
4. Output ONLY valid JSON, no markdown formatting

Required JSON schema:
{
    "direction": "LONG" | "SHORT" | "NO_TRADE",
    "confidence_score": number (0-100),
    "reasoning": "string (detailed technical and fundamental analysis)",
    "market_outlook": "string (short and mid-term outlook)",
    "entry_zone": {"min": number, "max": number},
    "stop_loss": number,
    "take_profit_targets": [number, number, number],
    "risk_reward_ratio": number,
    "risk_classification": "LOW" | "MEDIUM" | "HIGH",
    "timeframe": "string (e.g., 4h-1d)",
    "disclaimer": "string (risk warning)"
}"""

        user_prompt = f"""
Analyze {symbol} with the following data:

TECHNICAL INDICATORS:
- Current Price: ${technicals.get('current_price', 'N/A'):,.2f}
- RSI (14): {technicals.get('rsi', 'N/A'):.2f}
- MACD: {technicals.get('macd', 'N/A'):.2f}
- MACD Signal: {technicals.get('macd_signal', 'N/A'):.2f}
- EMA 20: ${technicals.get('ema_20', 'N/A'):,.2f}
- EMA 50: ${technicals.get('ema_50', 'N/A'):,.2f}
- EMA 200: ${technicals.get('ema_200', 'N/A'):,.2f}
- ATR (14): {technicals.get('atr', 'N/A'):.2f}
- Bollinger Upper: ${technicals.get('bb_upper', 'N/A'):,.2f}
- Bollinger Lower: ${technicals.get('bb_lower', 'N/A'):,.2f}
- Support: ${technicals.get('support', 'N/A'):,.2f}
- Resistance: ${technicals.get('resistance', 'N/A'):,.2f}
- Trend: {technicals.get('trend', 'N/A')}

MARKET CONTEXT:
- Fear & Greed Index: {context.get('fear_greed_index', 'N/A')} ({context.get('fear_greed_classification', 'N/A')})
- Funding Rate: {context.get('funding_rate', 'N/A')}
- Open Interest: ${context.get('open_interest', 'N/A'):,.0f}
- 24h Volume: ${context.get('24h_volume', 'N/A'):,.0f}

Provide your analysis in the required JSON format.
"""

        try:
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1000
            )
            
            signal_data = json.loads(completion.choices[0].message.content)
            
            # Add metadata
            signal_data["symbol"] = symbol
            signal_data["timestamp"] = pd.Timestamp.now().isoformat()
            signal_data["technicals_snapshot"] = technicals
            signal_data["context_snapshot"] = context
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
