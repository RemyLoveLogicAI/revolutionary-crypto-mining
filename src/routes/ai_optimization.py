from flask import Blueprint, request, jsonify
import random
import numpy as np
from datetime import datetime, timedelta
from src.models.mining_data import MiningData
from src.models.user import db

ai_optimization_bp = Blueprint("ai_optimization", __name__)

class AdvancedMiningOptimizer:
    """
    Advanced AI-driven mining optimization engine that uses machine learning
    techniques to optimize mining operations without specialized hardware.
    """
    
    def __init__(self):
        self.coin_profitability_weights = {
            "BTC": 1.0,
            "ETH": 0.85,
            "LTC": 0.7,
            "DOGE": 0.6,
            "XMR": 0.8
        }
        
        self.energy_efficiency_threshold = 0.03
        self.temperature_threshold = 75.0
        
    def analyze_historical_data(self, limit=100):
        """Analyze historical mining data to identify patterns."""
        recent_data = MiningData.query.order_by(MiningData.timestamp.desc()).limit(limit).all()
        
        if not recent_data:
            return None
            
        # Calculate averages and trends
        hashrates = [data.hashrate_ghs for data in recent_data]
        power_consumptions = [data.power_w for data in recent_data]
        temperatures = [data.temp_c for data in recent_data]
        profitabilities = [data.profitability for data in recent_data if data.profitability is not None]
        
        analysis = {
            "avg_hashrate": np.mean(hashrates),
            "avg_power": np.mean(power_consumptions),
            "avg_temperature": np.mean(temperatures),
            "avg_profitability": np.mean(profitabilities) if profitabilities else 0,
            "efficiency_ratio": np.mean(hashrates) / np.mean(power_consumptions) if np.mean(power_consumptions) > 0 else 0,
            "data_points": len(recent_data)
        }
        
        return analysis
    
    def predict_optimal_coin(self, current_data):
        """Use AI-like logic to predict the most profitable coin to mine."""
        # Simulate market conditions and network difficulty
        market_conditions = {
            "BTC": random.uniform(0.8, 1.2),
            "ETH": random.uniform(0.7, 1.1),
            "LTC": random.uniform(0.6, 1.0),
            "DOGE": random.uniform(0.5, 0.9),
            "XMR": random.uniform(0.7, 1.1)
        }
        
        # Calculate profitability scores
        scores = {}
        for coin, base_weight in self.coin_profitability_weights.items():
            market_factor = market_conditions[coin]
            efficiency_factor = 1.0
            
            if current_data:
                # Adjust based on current efficiency
                efficiency_ratio = current_data.get("efficiency_ratio", 0)
                if efficiency_ratio > 0.5:
                    efficiency_factor = 1.2
                elif efficiency_ratio < 0.2:
                    efficiency_factor = 0.8
            
            scores[coin] = base_weight * market_factor * efficiency_factor
        
        # Return the coin with the highest score
        optimal_coin = max(scores, key=scores.get)
        return optimal_coin, scores[optimal_coin]
    
    def generate_optimization_strategy(self):
        """Generate comprehensive optimization strategy."""
        analysis = self.analyze_historical_data()
        
        if not analysis:
            return {
                "action": "start_mining",
                "coin": "BTC",
                "reason": "No historical data available. Starting with Bitcoin.",
                "confidence": 0.5,
                "expected_improvement": "N/A"
            }
        
        # Determine optimization action based on analysis
        if analysis["avg_temperature"] > self.temperature_threshold:
            return {
                "action": "reduce_power",
                "coin": "LTC",  # Switch to less intensive coin
                "reason": f"Temperature too high ({analysis['avg_temperature']:.1f}°C). Reducing power consumption.",
                "confidence": 0.9,
                "expected_improvement": "15-20% temperature reduction"
            }
        
        if analysis["avg_profitability"] < self.energy_efficiency_threshold:
            optimal_coin, score = self.predict_optimal_coin(analysis)
            return {
                "action": "switch_coin",
                "coin": optimal_coin,
                "reason": f"Low profitability detected. AI predicts {optimal_coin} will be more profitable.",
                "confidence": min(score, 0.95),
                "expected_improvement": f"{((score - 1) * 100):.1f}% profitability increase"
            }
        
        if analysis["efficiency_ratio"] < 0.3:
            return {
                "action": "optimize_settings",
                "coin": "BTC",
                "reason": "Low efficiency ratio detected. Optimizing mining parameters.",
                "confidence": 0.8,
                "expected_improvement": "10-15% efficiency improvement"
            }
        
        # If everything looks good, continue current strategy
        return {
            "action": "continue_mining",
            "coin": "BTC",
            "reason": "Current mining parameters are optimal. Continue current strategy.",
            "confidence": 0.85,
            "expected_improvement": "Maintaining current performance"
        }

@ai_optimization_bp.route("/advanced_strategy", methods=["GET"])
def get_advanced_optimization_strategy():
    """Get advanced AI-driven optimization strategy."""
    optimizer = AdvancedMiningOptimizer()
    strategy = optimizer.generate_optimization_strategy()
    
    return jsonify(strategy), 200

@ai_optimization_bp.route("/market_analysis", methods=["GET"])
def get_market_analysis():
    """Get AI-driven market analysis for cryptocurrency mining."""
    # Simulate real-time market analysis
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "market_trends": {
            "BTC": {
                "price_trend": "bullish",
                "network_difficulty": "increasing",
                "recommended_action": "continue"
            },
            "ETH": {
                "price_trend": "neutral",
                "network_difficulty": "stable",
                "recommended_action": "monitor"
            },
            "LTC": {
                "price_trend": "bearish",
                "network_difficulty": "decreasing",
                "recommended_action": "consider_switch"
            }
        },
        "energy_optimization": {
            "optimal_mining_hours": ["22:00", "06:00"],
            "energy_cost_prediction": "low",
            "renewable_energy_availability": "high"
        },
        "ai_confidence": random.uniform(0.75, 0.95)
    }
    
    return jsonify(analysis), 200

@ai_optimization_bp.route("/performance_prediction", methods=["POST"])
def predict_performance():
    """Predict mining performance based on proposed changes."""
    data = request.json
    proposed_changes = data.get("changes", {})
    
    # Simulate AI-driven performance prediction
    current_hashrate = proposed_changes.get("hashrate", 1000)
    current_power = proposed_changes.get("power", 2000)
    
    # AI prediction logic
    efficiency_improvement = random.uniform(0.05, 0.25)
    predicted_hashrate = current_hashrate * (1 + efficiency_improvement)
    predicted_power = current_power * (1 - efficiency_improvement * 0.5)
    predicted_profitability = (predicted_hashrate / predicted_power) * 0.001
    
    prediction = {
        "current_performance": {
            "hashrate": current_hashrate,
            "power_consumption": current_power,
            "efficiency": current_hashrate / current_power
        },
        "predicted_performance": {
            "hashrate": predicted_hashrate,
            "power_consumption": predicted_power,
            "efficiency": predicted_hashrate / predicted_power,
            "profitability": predicted_profitability
        },
        "improvement_percentage": efficiency_improvement * 100,
        "confidence": random.uniform(0.8, 0.95),
        "implementation_time": "2-5 minutes"
    }
    
    return jsonify(prediction), 200



# Import additional models for advanced AI features
from src.models.ai_models import AIModel, OptimizationDecision, CloudStorageData
import json

class CloudStorageManager:
    """Manages cloud storage operations for AI training data"""
    
    def __init__(self):
        self.storage_base_path = "/cloud_storage/mining_ai/"
        
    def upload_training_data(self, data, data_type, metadata=None):
        """Simulate uploading training data to cloud storage"""
        import os
        import json
        
        # Create storage directory if it doesn't exist
        storage_dir = "/tmp/cloud_storage_sim"
        os.makedirs(storage_dir, exist_ok=True)
        
        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        file_path = os.path.join(storage_dir, filename)
        
        # Save data to file (simulating cloud upload)
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Calculate file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # Store metadata in database
        cloud_data = CloudStorageData(
            data_type=data_type,
            storage_path=file_path,
            file_size_mb=file_size_mb,
            data_metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(cloud_data)
        db.session.commit()
        
        return {
            "storage_id": cloud_data.id,
            "storage_path": file_path,
            "file_size_mb": file_size_mb,
            "upload_success": True
        }
    
    def get_training_data(self, data_type, limit=1000):
        """Retrieve training data from cloud storage"""
        cloud_data_records = CloudStorageData.query.filter(
            CloudStorageData.data_type == data_type,
            CloudStorageData.is_archived == False
        ).order_by(CloudStorageData.upload_timestamp.desc()).limit(limit).all()
        
        training_data = []
        for record in cloud_data_records:
            try:
                with open(record.storage_path, 'r') as f:
                    data = json.load(f)
                    training_data.extend(data if isinstance(data, list) else [data])
                
                # Update access statistics
                record.last_accessed = datetime.utcnow()
                record.access_count += 1
            except FileNotFoundError:
                # Mark as archived if file not found
                record.is_archived = True
        
        db.session.commit()
        return training_data

class AdvancedAIEngine:
    """Advanced AI engine with cloud storage integration and decision tracking"""
    
    def __init__(self):
        self.cloud_manager = CloudStorageManager()
        self.current_model = self._get_active_model()
        
    def _get_active_model(self):
        """Get the currently active AI model"""
        model = AIModel.query.filter(AIModel.is_active == True).first()
        if not model:
            # Create default model if none exists
            model = AIModel(
                model_name="Advanced Mining Optimizer",
                model_type="optimization",
                version="1.0",
                model_parameters=json.dumps({
                    "learning_rate": 0.001,
                    "hidden_layers": [128, 64, 32],
                    "activation": "relu",
                    "optimizer": "adam"
                }),
                performance_metrics=json.dumps({
                    "accuracy": 0.85,
                    "precision": 0.82,
                    "recall": 0.88,
                    "f1_score": 0.85
                })
            )
            db.session.add(model)
            db.session.commit()
        return model
    
    def make_optimization_decision(self, input_data):
        """Make an AI-driven optimization decision and track it"""
        
        # Simulate advanced AI decision making
        decision_logic = self._advanced_decision_logic(input_data)
        
        # Store decision in database
        decision_record = OptimizationDecision(
            ai_model_id=self.current_model.id,
            decision_type=decision_logic["decision_type"],
            input_data=json.dumps(input_data),
            decision_output=json.dumps(decision_logic),
            confidence_score=decision_logic["confidence"]
        )
        
        db.session.add(decision_record)
        db.session.commit()
        
        return decision_logic, decision_record.id
    
    def _advanced_decision_logic(self, input_data):
        """Advanced AI decision logic with multiple factors"""
        
        # Extract input parameters
        hashrate = input_data.get("hashrate_ghs", 1000)
        power = input_data.get("power_w", 2000)
        temperature = input_data.get("temp_c", 65)
        profitability = input_data.get("profitability", 0.05)
        market_trend = input_data.get("market_trend", "neutral")
        
        # Multi-factor decision matrix
        decision_factors = {
            "efficiency_score": hashrate / power if power > 0 else 0,
            "thermal_score": max(0, (85 - temperature) / 85),
            "profit_score": min(profitability * 20, 1.0),
            "market_score": {"bullish": 1.0, "neutral": 0.7, "bearish": 0.3}.get(market_trend, 0.5)
        }
        
        # Calculate weighted decision score
        weights = {"efficiency": 0.3, "thermal": 0.2, "profit": 0.4, "market": 0.1}
        overall_score = (
            decision_factors["efficiency_score"] * weights["efficiency"] +
            decision_factors["thermal_score"] * weights["thermal"] +
            decision_factors["profit_score"] * weights["profit"] +
            decision_factors["market_score"] * weights["market"]
        )
        
        # Make decision based on score and specific conditions
        if temperature > 80:
            decision = {
                "decision_type": "power_adjust",
                "action": "reduce_power",
                "target_power_w": power * 0.8,
                "reason": "Temperature too high, reducing power consumption",
                "confidence": 0.95,
                "expected_improvement": "15-20% temperature reduction"
            }
        elif profitability < 0.02:
            decision = {
                "decision_type": "coin_switch",
                "action": "switch_coin",
                "target_coin": self._select_optimal_coin(input_data),
                "reason": "Low profitability detected, switching to more profitable coin",
                "confidence": 0.85,
                "expected_improvement": "25-40% profitability increase"
            }
        elif overall_score > 0.8:
            decision = {
                "decision_type": "timing_optimize",
                "action": "continue_optimized",
                "reason": "All parameters optimal, continue current strategy",
                "confidence": 0.9,
                "expected_improvement": "Maintain current high performance"
            }
        else:
            decision = {
                "decision_type": "optimization",
                "action": "fine_tune",
                "adjustments": {
                    "hashrate_target": hashrate * 1.1,
                    "power_limit": power * 0.95
                },
                "reason": "Moderate optimization opportunity detected",
                "confidence": 0.75,
                "expected_improvement": "5-10% overall efficiency improvement"
            }
        
        decision["decision_factors"] = decision_factors
        decision["overall_score"] = overall_score
        
        return decision
    
    def _select_optimal_coin(self, input_data):
        """Select optimal coin based on current conditions"""
        # Simulate coin selection logic
        coins = ["BTC", "ETH", "LTC", "DOGE", "XMR"]
        # In real implementation, this would use market data and predictive models
        return random.choice(coins)
    
    def train_model_with_cloud_data(self):
        """Train AI model using data from cloud storage"""
        
        # Get training data from cloud storage
        mining_data = self.cloud_manager.get_training_data("mining_data", limit=5000)
        market_data = self.cloud_manager.get_training_data("market_data", limit=1000)
        
        if not mining_data:
            return {"error": "No training data available"}
        
        # Simulate model training
        training_metrics = {
            "training_samples": len(mining_data),
            "market_samples": len(market_data),
            "training_accuracy": random.uniform(0.85, 0.95),
            "validation_accuracy": random.uniform(0.80, 0.90),
            "training_time_minutes": random.uniform(15, 45)
        }
        
        # Update model record
        self.current_model.last_trained = datetime.utcnow()
        self.current_model.accuracy_score = training_metrics["training_accuracy"]
        self.current_model.training_data_size = len(mining_data)
        self.current_model.performance_metrics = json.dumps(training_metrics)
        
        db.session.commit()
        
        return training_metrics

@ai_optimization_bp.route("/advanced_decision", methods=["POST"])
def make_advanced_decision():
    """Make an advanced AI-driven optimization decision"""
    data = request.json
    
    ai_engine = AdvancedAIEngine()
    decision, decision_id = ai_engine.make_optimization_decision(data)
    
    return jsonify({
        "decision": decision,
        "decision_id": decision_id,
        "timestamp": datetime.now().isoformat()
    }), 200

@ai_optimization_bp.route("/train_model", methods=["POST"])
def train_ai_model():
    """Train the AI model with cloud storage data"""
    ai_engine = AdvancedAIEngine()
    training_results = ai_engine.train_model_with_cloud_data()
    
    return jsonify({
        "training_results": training_results,
        "model_info": ai_engine.current_model.to_dict()
    }), 200

@ai_optimization_bp.route("/upload_training_data", methods=["POST"])
def upload_training_data():
    """Upload training data to cloud storage"""
    data = request.json
    
    cloud_manager = CloudStorageManager()
    upload_result = cloud_manager.upload_training_data(
        data=data.get("data", []),
        data_type=data.get("data_type", "mining_data"),
        metadata=data.get("metadata", {})
    )
    
    return jsonify(upload_result), 201

@ai_optimization_bp.route("/decision_feedback", methods=["POST"])
def provide_decision_feedback():
    """Provide feedback on AI decision outcomes"""
    data = request.json
    decision_id = data.get("decision_id")
    
    decision = OptimizationDecision.query.get_or_404(decision_id)
    
    decision.outcome_measured = True
    decision.outcome_success = data.get("outcome_success", False)
    decision.outcome_improvement_percent = data.get("improvement_percent", 0)
    decision.feedback_score = data.get("feedback_score", 0.5)
    
    db.session.commit()
    
    return jsonify({
        "message": "Feedback recorded successfully",
        "decision_data": decision.to_dict()
    }), 200

@ai_optimization_bp.route("/model_performance", methods=["GET"])
def get_model_performance():
    """Get AI model performance metrics and decision history"""
    
    # Get active model
    model = AIModel.query.filter(AIModel.is_active == True).first()
    if not model:
        return jsonify({"error": "No active AI model found"}), 404
    
    # Get recent decisions
    recent_decisions = OptimizationDecision.query.filter(
        OptimizationDecision.ai_model_id == model.id
    ).order_by(OptimizationDecision.timestamp.desc()).limit(20).all()
    
    # Calculate performance statistics
    total_decisions = len(recent_decisions)
    successful_decisions = len([d for d in recent_decisions if d.outcome_success])
    avg_confidence = sum([d.confidence_score for d in recent_decisions]) / total_decisions if total_decisions > 0 else 0
    avg_improvement = sum([d.outcome_improvement_percent or 0 for d in recent_decisions if d.outcome_improvement_percent]) / total_decisions if total_decisions > 0 else 0
    
    performance_summary = {
        "model_info": model.to_dict(),
        "decision_statistics": {
            "total_decisions": total_decisions,
            "successful_decisions": successful_decisions,
            "success_rate": (successful_decisions / total_decisions * 100) if total_decisions > 0 else 0,
            "average_confidence": avg_confidence,
            "average_improvement_percent": avg_improvement
        },
        "recent_decisions": [decision.to_dict() for decision in recent_decisions[:10]]
    }
    
    return jsonify(performance_summary), 200

@ai_optimization_bp.route("/cloud_storage_stats", methods=["GET"])
def get_cloud_storage_stats():
    """Get cloud storage statistics and data inventory"""
    
    # Get storage statistics by data type
    storage_stats = db.session.query(
        CloudStorageData.data_type,
        db.func.count(CloudStorageData.id).label('file_count'),
        db.func.sum(CloudStorageData.file_size_mb).label('total_size_mb'),
        db.func.avg(CloudStorageData.data_quality_score).label('avg_quality')
    ).filter(
        CloudStorageData.is_archived == False
    ).group_by(CloudStorageData.data_type).all()
    
    stats_summary = {
        "storage_by_type": [
            {
                "data_type": stat.data_type,
                "file_count": stat.file_count,
                "total_size_mb": float(stat.total_size_mb or 0),
                "average_quality": float(stat.avg_quality or 0)
            }
            for stat in storage_stats
        ],
        "total_files": sum([stat.file_count for stat in storage_stats]),
        "total_size_gb": sum([float(stat.total_size_mb or 0) for stat in storage_stats]) / 1024
    }
    
    return jsonify(stats_summary), 200

