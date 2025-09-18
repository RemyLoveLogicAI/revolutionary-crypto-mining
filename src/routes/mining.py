from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
from src.models.mining_data import MiningData
from src.models.profitability import ProfitabilityData, MiningSession
from src.models.user import db

mining_bp = Blueprint("mining", __name__)

@mining_bp.route("/data", methods=["POST"])
def receive_mining_data():
    data = request.json
    new_data = MiningData(
        timestamp=data.get("timestamp"),
        hashrate_ghs=data.get("hashrate_ghs"),
        power_w=data.get("power_w"),
        temp_c=data.get("temp_c"),
        fan_speed_percent=data.get("fan_speed_percent"),
        errors=data.get("errors"),
        profitability=data.get("profitability")
    )

    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data received and stored successfully"}), 201

@mining_bp.route("/optimization", methods=["GET"])
def get_optimization_strategy():
    # This is a very basic AI-like optimization based on dummy data
    # In a real scenario, this would involve more complex ML models
    last_data = MiningData.query.order_by(MiningData.timestamp.desc()).first()

    if last_data:
        # Simple logic: if profitability is low, suggest switching coin
        # This is a placeholder for a real AI model
        if last_data.profitability < 0.03: # Assuming profitability is stored in the DB
            strategy = {
                "action": "switch_coin",
                "coin": "LTC", # Suggest switching to Litecoin
                "reason": "Profitability is low, consider alternative coins."
            }
        else:
            strategy = {
                "action": "continue_mining",
                "coin": "BTC", # Continue mining Bitcoin
                "reason": "Current profitability is satisfactory."
            }
    else:
        strategy = {
            "action": "start_mining",
            "coin": "BTC",
            "reason": "No data available, starting with default."
        }
    return jsonify(strategy), 200

@mining_bp.route("/status", methods=["GET"])
def get_mining_status():
    last_data = MiningData.query.order_by(MiningData.timestamp.desc()).first()

    if last_data:
        status = {
            "hashrate": f"{last_data.hashrate_ghs:.2f} GH/s",
            "power_consumption": f"{last_data.power_w:.2f} W",
            "temperature": f"{last_data.temp_c:.2f} C",
            "profitability": f"{last_data.profitability:.4f} BTC/day" if last_data.profitability is not None else "N/A"
        }
    else:
        status = {
            "hashrate": "N/A",
            "power_consumption": "N/A",
            "temperature": "N/A",
            "profitability": "N/A"
        }
    return jsonify(status), 200




def calculate_profitability(hashrate_ghs, power_w, coin_type='BTC'):
    """Calculate detailed profitability metrics for mining operations"""
    
    # Simulated market data (in real implementation, this would come from APIs)
    market_data = {
        'BTC': {'price': 45000, 'difficulty': 50000000000000, 'block_reward': 6.25},
        'ETH': {'price': 3000, 'difficulty': 15000000000000000, 'block_reward': 2.0},
        'LTC': {'price': 150, 'difficulty': 20000000, 'block_reward': 12.5},
        'DOGE': {'price': 0.08, 'difficulty': 8000000, 'block_reward': 10000},
        'XMR': {'price': 200, 'difficulty': 300000000000, 'block_reward': 0.6}
    }
    
    coin_data = market_data.get(coin_type, market_data['BTC'])
    energy_cost_per_kwh = 0.12  # $0.12 per kWh
    
    # Calculate daily metrics
    daily_power_kwh = (power_w * 24) / 1000
    daily_energy_cost = daily_power_kwh * energy_cost_per_kwh
    
    # Simplified mining reward calculation
    network_hashrate = coin_data['difficulty'] * 1000000  # Simplified conversion
    mining_share = hashrate_ghs / (network_hashrate / 1000000000)  # Convert to GH/s
    daily_coins = coin_data['block_reward'] * mining_share * 144  # Assuming 144 blocks per day
    daily_revenue = daily_coins * coin_data['price']
    
    daily_profit = daily_revenue - daily_energy_cost
    profit_margin = (daily_profit / daily_revenue * 100) if daily_revenue > 0 else 0
    
    return {
        'coin_price_usd': coin_data['price'],
        'network_difficulty': coin_data['difficulty'],
        'block_reward': coin_data['block_reward'],
        'daily_revenue_usd': daily_revenue,
        'daily_cost_usd': daily_energy_cost,
        'daily_profit_usd': daily_profit,
        'profit_margin_percent': profit_margin,
        'roi_days': (2000 / daily_profit) if daily_profit > 0 else None  # Assuming $2000 hardware cost
    }

@mining_bp.route("/profitability", methods=["POST"])
def store_profitability_data():
    """Store detailed profitability data"""
    data = request.json
    
    # Calculate profitability metrics
    profitability_metrics = calculate_profitability(
        data.get("hashrate_ghs", 1000),
        data.get("power_w", 2000),
        data.get("coin_type", "BTC")
    )
    
    # Create profitability record
    profitability_data = ProfitabilityData(
        coin_type=data.get("coin_type", "BTC"),
        hashrate_ghs=data.get("hashrate_ghs", 1000),
        power_consumption_w=data.get("power_w", 2000),
        energy_cost_per_kwh=data.get("energy_cost_per_kwh", 0.12),
        **profitability_metrics
    )
    
    db.session.add(profitability_data)
    db.session.commit()
    
    return jsonify({
        "message": "Profitability data stored successfully",
        "profitability_metrics": profitability_metrics
    }), 201

@mining_bp.route("/profitability/analysis", methods=["GET"])
def get_profitability_analysis():
    """Get comprehensive profitability analysis"""
    days = request.args.get('days', 7, type=int)
    coin_type = request.args.get('coin_type', 'BTC')
    
    # Get recent profitability data
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    profitability_data = ProfitabilityData.query.filter(
        ProfitabilityData.timestamp >= cutoff_date,
        ProfitabilityData.coin_type == coin_type
    ).order_by(ProfitabilityData.timestamp.desc()).all()
    
    if not profitability_data:
        return jsonify({
            "message": "No profitability data available",
            "analysis": None
        }), 200
    
    # Calculate analysis metrics
    profits = [data.daily_profit_usd for data in profitability_data]
    revenues = [data.daily_revenue_usd for data in profitability_data]
    costs = [data.daily_cost_usd for data in profitability_data]
    margins = [data.profit_margin_percent for data in profitability_data]
    
    analysis = {
        "period_days": days,
        "coin_type": coin_type,
        "total_data_points": len(profitability_data),
        "average_daily_profit": sum(profits) / len(profits),
        "average_daily_revenue": sum(revenues) / len(revenues),
        "average_daily_cost": sum(costs) / len(costs),
        "average_profit_margin": sum(margins) / len(margins),
        "total_profit": sum(profits),
        "best_day_profit": max(profits),
        "worst_day_profit": min(profits),
        "profitability_trend": "increasing" if profits[0] > profits[-1] else "decreasing",
        "data": [data.to_dict() for data in profitability_data[:10]]  # Last 10 records
    }
    
    return jsonify(analysis), 200

@mining_bp.route("/sessions", methods=["POST"])
def start_mining_session():
    """Start a new mining session"""
    data = request.json
    
    session = MiningSession(
        coin_type=data.get("coin_type", "BTC"),
        total_hashrate_ghs=data.get("hashrate_ghs", 1000),
        total_power_w=data.get("power_w", 2000)
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        "message": "Mining session started",
        "session_id": session.id,
        "session_data": session.to_dict()
    }), 201

@mining_bp.route("/sessions/<int:session_id>", methods=["PUT"])
def end_mining_session(session_id):
    """End a mining session and calculate final metrics"""
    data = request.json
    
    session = MiningSession.query.get_or_404(session_id)
    session.session_end = datetime.utcnow()
    
    # Calculate session duration
    duration = session.session_end - session.session_start
    session.session_duration_hours = duration.total_seconds() / 3600
    
    # Update session metrics
    session.total_revenue_usd = data.get("total_revenue_usd", 0)
    session.total_cost_usd = data.get("total_cost_usd", 0)
    session.total_profit_usd = session.total_revenue_usd - session.total_cost_usd
    session.average_temperature_c = data.get("average_temperature_c", 65)
    session.uptime_percent = data.get("uptime_percent", 95)
    session.errors_count = data.get("errors_count", 0)
    
    db.session.commit()
    
    return jsonify({
        "message": "Mining session ended",
        "session_data": session.to_dict()
    }), 200

@mining_bp.route("/sessions", methods=["GET"])
def get_mining_sessions():
    """Get mining sessions history"""
    limit = request.args.get('limit', 10, type=int)
    coin_type = request.args.get('coin_type')
    
    query = MiningSession.query
    if coin_type:
        query = query.filter(MiningSession.coin_type == coin_type)
    
    sessions = query.order_by(MiningSession.session_start.desc()).limit(limit).all()
    
    return jsonify({
        "sessions": [session.to_dict() for session in sessions],
        "total_sessions": len(sessions)
    }), 200

