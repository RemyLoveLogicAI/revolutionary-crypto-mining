from .user import db

class MiningData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100), nullable=False)
    hashrate_ghs = db.Column(db.Float, nullable=False)
    power_w = db.Column(db.Float, nullable=False)
    temp_c = db.Column(db.Float, nullable=False)
    fan_speed_percent = db.Column(db.Integer, nullable=False)
    errors = db.Column(db.Integer, nullable=False)
    profitability = db.Column(db.Float, nullable=True)
    def __repr__(self):
        return f"<MiningData {self.id}>"


