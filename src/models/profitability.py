from .user import db
from datetime import datetime

class ProfitabilityData(db.Model):
    """Model for tracking detailed profitability metrics"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    coin_type = db.Column(db.String(10), nullable=False, default='BTC')
    hashrate_ghs = db.Column(db.Float, nullable=False)
    power_consumption_w = db.Column(db.Float, nullable=False)
    energy_cost_per_kwh = db.Column(db.Float, nullable=False, default=0.12)
    coin_price_usd = db.Column(db.Float, nullable=False)
    network_difficulty = db.Column(db.Float, nullable=False)
    block_reward = db.Column(db.Float, nullable=False)
    daily_revenue_usd = db.Column(db.Float, nullable=False)
    daily_cost_usd = db.Column(db.Float, nullable=False)
    daily_profit_usd = db.Column(db.Float, nullable=False)
    profit_margin_percent = db.Column(db.Float, nullable=False)
    roi_days = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f"<ProfitabilityData {self.coin_type} - {self.timestamp}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'coin_type': self.coin_type,
            'hashrate_ghs': self.hashrate_ghs,
            'power_consumption_w': self.power_consumption_w,
            'energy_cost_per_kwh': self.energy_cost_per_kwh,
            'coin_price_usd': self.coin_price_usd,
            'network_difficulty': self.network_difficulty,
            'block_reward': self.block_reward,
            'daily_revenue_usd': self.daily_revenue_usd,
            'daily_cost_usd': self.daily_cost_usd,
            'daily_profit_usd': self.daily_profit_usd,
            'profit_margin_percent': self.profit_margin_percent,
            'roi_days': self.roi_days
        }

class MiningSession(db.Model):
    """Model for tracking mining sessions and their performance"""
    id = db.Column(db.Integer, primary_key=True)
    session_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    session_end = db.Column(db.DateTime, nullable=True)
    coin_type = db.Column(db.String(10), nullable=False, default='BTC')
    total_hashrate_ghs = db.Column(db.Float, nullable=False)
    total_power_w = db.Column(db.Float, nullable=False)
    total_revenue_usd = db.Column(db.Float, nullable=False, default=0.0)
    total_cost_usd = db.Column(db.Float, nullable=False, default=0.0)
    total_profit_usd = db.Column(db.Float, nullable=False, default=0.0)
    session_duration_hours = db.Column(db.Float, nullable=True)
    average_temperature_c = db.Column(db.Float, nullable=True)
    uptime_percent = db.Column(db.Float, nullable=True)
    errors_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<MiningSession {self.coin_type} - {self.session_start}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'coin_type': self.coin_type,
            'total_hashrate_ghs': self.total_hashrate_ghs,
            'total_power_w': self.total_power_w,
            'total_revenue_usd': self.total_revenue_usd,
            'total_cost_usd': self.total_cost_usd,
            'total_profit_usd': self.total_profit_usd,
            'session_duration_hours': self.session_duration_hours,
            'average_temperature_c': self.average_temperature_c,
            'uptime_percent': self.uptime_percent,
            'errors_count': self.errors_count
        }

