from typing import Dict

class RiskEngine:
    @staticmethod
    def calculate_position_size(
        capital: float,
        risk_percentage: float,  # e.g., 0.02 for 2%
        entry_price: float,
        stop_loss_price: float
    ) -> Dict:
        """
        Calculates position size ensuring max loss equals risk percentage.
        Formula: Position Size = (Capital * Risk%) / |Entry - Stop Loss|
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            raise ValueError("Invalid price parameters")
        
        if entry_price == stop_loss_price:
            raise ValueError("Entry price cannot equal stop loss")

        risk_amount = capital * risk_percentage
        price_diff = abs(entry_price - stop_loss_price)
        
        # Position size in base currency (e.g., BTC)
        position_size_base = risk_amount / price_diff
        
        # Position size in quote currency (e.g., USDT)
        position_size_quote = position_size_base * entry_price
        
        # Leverage calculation
        leverage = position_size_quote / capital if capital > 0 else 1
        
        return {
            "position_size_base": round(position_size_base, 8),
            "position_size_quote": round(position_size_quote, 2),
            "risk_amount_usd": round(risk_amount, 2),
            "max_loss_usd": round(risk_amount, 2),  # By definition
            "leverage_required": round(leverage, 2),
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "risk_percentage": risk_percentage * 100
        }

    @staticmethod
    def calculate_risk_reward(entry: float, stop_loss: float, take_profits: list) -> Dict:
        """Calculates risk-reward ratio for multiple TP targets"""
        risk = abs(entry - stop_loss)
        
        rewards = []
        for tp in take_profits:
            reward = abs(tp - entry)
            rr_ratio = reward / risk if risk > 0 else 0
            rewards.append({
                "take_profit": tp,
                "reward": round(reward, 2),
                "risk_reward_ratio": round(rr_ratio, 2)
            })
        
        avg_rr = sum(r['risk_reward_ratio'] for r in rewards) / len(rewards) if rewards else 0
        
        return {
            "risk": round(risk, 2),
            "take_profit_levels": rewards,
            "average_rr_ratio": round(avg_rr, 2)
        }
