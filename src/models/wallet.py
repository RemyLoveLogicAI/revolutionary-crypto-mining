from src.models.user import db
from datetime import datetime
from enum import Enum

class CryptoCurrency(Enum):
    BITCOIN = 'BTC'
    ETHEREUM = 'ETH'
    LITECOIN = 'LTC'
    DOGECOIN = 'DOGE'
    MONERO = 'XMR'
    USDT = 'USDT'
    USDC = 'USDC'

class PayoutStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class UserWallet(db.Model):
    __tablename__ = 'user_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.Enum(CryptoCurrency), nullable=False)
    wallet_address = db.Column(db.String(255), nullable=False)
    wallet_label = db.Column(db.String(100), nullable=True)  # User-friendly label
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='wallets')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'currency': self.currency.value,
            'wallet_address': self.wallet_address,
            'wallet_label': self.wallet_label,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PayoutRequest(db.Model):
    __tablename__ = 'payout_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('user_wallets.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in cryptocurrency
    currency = db.Column(db.Enum(CryptoCurrency), nullable=False)
    usd_value = db.Column(db.Float, nullable=True)  # USD value at time of request
    status = db.Column(db.Enum(PayoutStatus), default=PayoutStatus.PENDING)
    
    # Payment gateway fields
    gateway_transaction_id = db.Column(db.String(255), nullable=True)
    gateway_response = db.Column(db.Text, nullable=True)  # JSON response from gateway
    
    # Timestamps
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref='payout_requests')
    wallet = db.relationship('UserWallet', backref='payout_requests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'amount': self.amount,
            'currency': self.currency.value,
            'usd_value': self.usd_value,
            'status': self.status.value,
            'gateway_transaction_id': self.gateway_transaction_id,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count
        }

class EarningsBalance(db.Model):
    __tablename__ = 'earnings_balance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.Enum(CryptoCurrency), nullable=False)
    available_balance = db.Column(db.Float, default=0.0)  # Available for payout
    pending_balance = db.Column(db.Float, default=0.0)    # Pending confirmation
    total_earned = db.Column(db.Float, default=0.0)       # Total lifetime earnings
    total_paid_out = db.Column(db.Float, default=0.0)     # Total paid out
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='earnings_balances')
    
    # Unique constraint to ensure one balance per user per currency
    __table_args__ = (db.UniqueConstraint('user_id', 'currency', name='unique_user_currency_balance'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'currency': self.currency.value,
            'available_balance': self.available_balance,
            'pending_balance': self.pending_balance,
            'total_earned': self.total_earned,
            'total_paid_out': self.total_paid_out,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class PayoutTransaction(db.Model):
    __tablename__ = 'payout_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    payout_request_id = db.Column(db.Integer, db.ForeignKey('payout_requests.id'), nullable=False)
    transaction_hash = db.Column(db.String(255), nullable=True)  # Blockchain transaction hash
    block_number = db.Column(db.Integer, nullable=True)
    confirmations = db.Column(db.Integer, default=0)
    network_fee = db.Column(db.Float, nullable=True)  # Network fee paid
    gateway_fee = db.Column(db.Float, nullable=True)  # Gateway fee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    payout_request = db.relationship('PayoutRequest', backref='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'payout_request_id': self.payout_request_id,
            'transaction_hash': self.transaction_hash,
            'block_number': self.block_number,
            'confirmations': self.confirmations,
            'network_fee': self.network_fee,
            'gateway_fee': self.gateway_fee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }
