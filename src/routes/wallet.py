from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.user import db
from src.models.wallet import (
    UserWallet, PayoutRequest, EarningsBalance, PayoutTransaction,
    CryptoCurrency, PayoutStatus
)
from src.services.crypto_gateway import CryptoPaymentGateway
import random

wallet_bp = Blueprint('wallet', __name__)

# Initialize payment gateway (sandbox mode for demo)
payment_gateway = CryptoPaymentGateway(sandbox=True)

@wallet_bp.route('/wallets', methods=['GET'])
def get_user_wallets():
    """Get all wallets for a user"""
    user_id = request.args.get('user_id', 1)  # Default user for demo
    
    wallets = UserWallet.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({
        'wallets': [wallet.to_dict() for wallet in wallets],
        'count': len(wallets)
    })

@wallet_bp.route('/wallets', methods=['POST'])
def add_wallet():
    """Add a new wallet address for a user"""
    data = request.get_json()
    
    required_fields = ['currency', 'wallet_address']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        currency = CryptoCurrency(data['currency'])
    except ValueError:
        return jsonify({'error': 'Invalid currency'}), 400
    
    # Validate wallet address
    if not payment_gateway.validate_wallet_address(data['wallet_address'], currency):
        return jsonify({'error': 'Invalid wallet address format'}), 400
    
    # Check if wallet already exists
    existing_wallet = UserWallet.query.filter_by(
        user_id=data.get('user_id', 1),
        currency=currency,
        wallet_address=data['wallet_address']
    ).first()
    
    if existing_wallet:
        return jsonify({'error': 'Wallet address already exists'}), 400
    
    # Create new wallet
    wallet = UserWallet(
        user_id=data.get('user_id', 1),
        currency=currency,
        wallet_address=data['wallet_address'],
        wallet_label=data.get('wallet_label', f"{currency.value} Wallet"),
        is_verified=True  # Auto-verify for demo
    )
    
    db.session.add(wallet)
    db.session.commit()
    
    return jsonify({
        'message': 'Wallet added successfully',
        'wallet': wallet.to_dict()
    }), 201

@wallet_bp.route('/wallets/<int:wallet_id>', methods=['DELETE'])
def remove_wallet(wallet_id):
    """Remove (deactivate) a wallet"""
    wallet = UserWallet.query.get_or_404(wallet_id)
    wallet.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Wallet removed successfully'})

@wallet_bp.route('/balance', methods=['GET'])
def get_earnings_balance():
    """Get user's earnings balance"""
    user_id = request.args.get('user_id', 1)
    
    balances = EarningsBalance.query.filter_by(user_id=user_id).all()
    
    # Create demo balances if none exist
    if not balances:
        demo_balances = [
            EarningsBalance(user_id=user_id, currency=CryptoCurrency.BITCOIN, 
                          available_balance=0.0125, total_earned=0.0250),
            EarningsBalance(user_id=user_id, currency=CryptoCurrency.ETHEREUM, 
                          available_balance=0.185, total_earned=0.370),
            EarningsBalance(user_id=user_id, currency=CryptoCurrency.USDT, 
                          available_balance=125.50, total_earned=250.00)
        ]
        
        for balance in demo_balances:
            db.session.add(balance)
        db.session.commit()
        balances = demo_balances
    
    return jsonify({
        'balances': [balance.to_dict() for balance in balances],
        'total_usd_value': sum([
            balance.available_balance * get_usd_rate(balance.currency) 
            for balance in balances
        ])
    })

@wallet_bp.route('/payout', methods=['POST'])
def request_payout():
    """Request a cryptocurrency payout"""
    data = request.get_json()
    
    required_fields = ['wallet_id', 'amount', 'currency']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        currency = CryptoCurrency(data['currency'])
        amount = float(data['amount'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid currency or amount'}), 400
    
    # Get wallet
    wallet = UserWallet.query.get_or_404(data['wallet_id'])
    if not wallet.is_active:
        return jsonify({'error': 'Wallet is not active'}), 400
    
    # Check minimum payout amount
    min_payout = payment_gateway.get_minimum_payout(currency)
    if amount < min_payout:
        return jsonify({
            'error': f'Amount below minimum payout of {min_payout} {currency.value}'
        }), 400
    
    # Check user balance
    user_balance = EarningsBalance.query.filter_by(
        user_id=wallet.user_id, 
        currency=currency
    ).first()
    
    if not user_balance or user_balance.available_balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Calculate fees
    fee_info = payment_gateway.calculate_payout_fees(amount, currency)
    
    # Create payout request
    payout_request = PayoutRequest(
        user_id=wallet.user_id,
        wallet_id=wallet.id,
        amount=amount,
        currency=currency,
        usd_value=amount * get_usd_rate(currency),
        status=PayoutStatus.PENDING
    )
    
    db.session.add(payout_request)
    db.session.flush()  # Get the ID
    
    # Process payout through gateway
    gateway_response = payment_gateway.create_payout(
        wallet.wallet_address,
        amount,
        currency,
        f"payout_request_{payout_request.id}"
    )
    
    if gateway_response.get('success'):
        payout_request.gateway_transaction_id = gateway_response.get('transaction_id')
        payout_request.status = PayoutStatus.PROCESSING
        payout_request.processed_at = datetime.utcnow()
        
        # Update user balance
        user_balance.available_balance -= amount
        user_balance.total_paid_out += amount
        
        # Create transaction record
        transaction = PayoutTransaction(
            payout_request_id=payout_request.id,
            network_fee=gateway_response.get('network_fee', 0),
            gateway_fee=gateway_response.get('gateway_fee', 0)
        )
        db.session.add(transaction)
        
    else:
        payout_request.status = PayoutStatus.FAILED
        payout_request.error_message = gateway_response.get('error', 'Unknown error')
    
    payout_request.gateway_response = str(gateway_response)
    db.session.commit()
    
    return jsonify({
        'message': 'Payout request created successfully',
        'payout_request': payout_request.to_dict(),
        'fee_info': fee_info,
        'gateway_response': gateway_response
    }), 201

@wallet_bp.route('/payouts', methods=['GET'])
def get_payout_history():
    """Get payout history for a user"""
    user_id = request.args.get('user_id', 1)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    payouts = PayoutRequest.query.filter_by(user_id=user_id)\
        .order_by(PayoutRequest.requested_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'payouts': [payout.to_dict() for payout in payouts.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': payouts.total,
            'pages': payouts.pages
        }
    })

@wallet_bp.route('/payouts/<int:payout_id>/status', methods=['GET'])
def check_payout_status(payout_id):
    """Check the status of a specific payout"""
    payout = PayoutRequest.query.get_or_404(payout_id)
    
    if payout.gateway_transaction_id and payout.status == PayoutStatus.PROCESSING:
        # Check status with payment gateway
        gateway_status = payment_gateway.get_payout_status(payout.gateway_transaction_id)
        
        if gateway_status.get('success'):
            status = gateway_status.get('status')
            
            if status == 'completed' and payout.status != PayoutStatus.COMPLETED:
                payout.status = PayoutStatus.COMPLETED
                payout.completed_at = datetime.utcnow()
                
                # Update transaction record
                transaction = PayoutTransaction.query.filter_by(
                    payout_request_id=payout.id
                ).first()
                if transaction:
                    transaction.transaction_hash = gateway_status.get('transaction_hash')
                    transaction.block_number = gateway_status.get('block_number')
                    transaction.confirmations = gateway_status.get('confirmations', 0)
                    transaction.confirmed_at = datetime.utcnow()
                
                db.session.commit()
            
            elif status == 'failed' and payout.status != PayoutStatus.FAILED:
                payout.status = PayoutStatus.FAILED
                payout.error_message = gateway_status.get('error_message', 'Transaction failed')
                db.session.commit()
    
    return jsonify({
        'payout': payout.to_dict(),
        'transactions': [tx.to_dict() for tx in payout.transactions]
    })

@wallet_bp.route('/supported-currencies', methods=['GET'])
def get_supported_currencies():
    """Get list of supported cryptocurrencies"""
    currencies = []
    for currency in CryptoCurrency:
        if payment_gateway.is_currency_supported(currency):
            currencies.append({
                'code': currency.value,
                'name': currency.name.title(),
                'min_payout': payment_gateway.get_minimum_payout(currency),
                'network_fee': payment_gateway.get_network_fee(currency)
            })
    
    return jsonify({'supported_currencies': currencies})

@wallet_bp.route('/exchange-rates', methods=['GET'])
def get_exchange_rates():
    """Get current cryptocurrency exchange rates"""
    rates_response = payment_gateway.get_exchange_rates()
    return jsonify(rates_response)

def get_usd_rate(currency: CryptoCurrency) -> float:
    """Get USD exchange rate for a currency (mock data)"""
    mock_rates = {
        CryptoCurrency.BITCOIN: 45000.00,
        CryptoCurrency.ETHEREUM: 3000.00,
        CryptoCurrency.LITECOIN: 100.00,
        CryptoCurrency.DOGECOIN: 0.08,
        CryptoCurrency.USDT: 1.00,
        CryptoCurrency.USDC: 1.00
    }
    return mock_rates.get(currency, 1.00)
