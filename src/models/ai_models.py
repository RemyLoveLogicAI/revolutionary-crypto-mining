from .user import db
from datetime import datetime
import json

class AIModel(db.Model):
    """Model for storing AI model metadata and performance metrics"""
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # 'optimization', 'prediction', 'anomaly_detection'
    version = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_trained = db.Column(db.DateTime, nullable=True)
    accuracy_score = db.Column(db.Float, nullable=True)
    training_data_size = db.Column(db.Integer, nullable=True)
    model_parameters = db.Column(db.Text, nullable=True)  # JSON string of model parameters
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    performance_metrics = db.Column(db.Text, nullable=True)  # JSON string of performance metrics
    
    def __repr__(self):
        return f"<AIModel {self.model_name} v{self.version}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_type': self.model_type,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'last_trained': self.last_trained.isoformat() if self.last_trained else None,
            'accuracy_score': self.accuracy_score,
            'training_data_size': self.training_data_size,
            'model_parameters': json.loads(self.model_parameters) if self.model_parameters else None,
            'is_active': self.is_active,
            'performance_metrics': json.loads(self.performance_metrics) if self.performance_metrics else None
        }

class OptimizationDecision(db.Model):
    """Model for tracking AI optimization decisions and their outcomes"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'), nullable=False)
    decision_type = db.Column(db.String(50), nullable=False)  # 'coin_switch', 'power_adjust', 'timing_optimize'
    input_data = db.Column(db.Text, nullable=False)  # JSON string of input data used for decision
    decision_output = db.Column(db.Text, nullable=False)  # JSON string of AI decision
    confidence_score = db.Column(db.Float, nullable=False)
    implemented = db.Column(db.Boolean, nullable=False, default=False)
    outcome_measured = db.Column(db.Boolean, nullable=False, default=False)
    outcome_success = db.Column(db.Boolean, nullable=True)
    outcome_improvement_percent = db.Column(db.Float, nullable=True)
    feedback_score = db.Column(db.Float, nullable=True)  # User or system feedback on decision quality
    
    ai_model = db.relationship('AIModel', backref=db.backref('decisions', lazy=True))
    
    def __repr__(self):
        return f"<OptimizationDecision {self.decision_type} - {self.timestamp}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'ai_model_id': self.ai_model_id,
            'decision_type': self.decision_type,
            'input_data': json.loads(self.input_data) if self.input_data else None,
            'decision_output': json.loads(self.decision_output) if self.decision_output else None,
            'confidence_score': self.confidence_score,
            'implemented': self.implemented,
            'outcome_measured': self.outcome_measured,
            'outcome_success': self.outcome_success,
            'outcome_improvement_percent': self.outcome_improvement_percent,
            'feedback_score': self.feedback_score
        }

class CloudStorageData(db.Model):
    """Model for tracking data stored in cloud storage for AI training"""
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(50), nullable=False)  # 'mining_data', 'market_data', 'model_weights'
    storage_path = db.Column(db.String(500), nullable=False)
    file_size_mb = db.Column(db.Float, nullable=False)
    upload_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    access_count = db.Column(db.Integer, nullable=False, default=0)
    data_quality_score = db.Column(db.Float, nullable=True)
    data_metadata = db.Column(db.Text, nullable=True)  # JSON string of additional metadata
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<CloudStorageData {self.data_type} - {self.storage_path}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_type': self.data_type,
            'storage_path': self.storage_path,
            'file_size_mb': self.file_size_mb,
            'upload_timestamp': self.upload_timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count,
            'data_quality_score': self.data_quality_score,
            'metadata': json.loads(self.data_metadata) if self.data_metadata else None,
            'is_archived': self.is_archived
        }

