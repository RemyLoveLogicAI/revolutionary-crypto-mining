import requests
import json
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, Optional, List
from src.models.wallet import CryptoCurrency, PayoutStatus

class CryptoPaymentGateway:
    """
    Cryptocurrency payment gateway service for handling payouts.
    This is a mock implementation that simulates a real payment gateway.
    In production, this would integrate with services like BitPay, Coinbase Commerce, or similar.
    """
    
    def __init__(self, api_key: str = "demo_api_key", api_secret: str = "demo_secret", sandbox: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        self.base_url = "https://api-sandbox.cryptogateway.com" if sandbox else "https://api.cryptogateway.com"
        
        # Supported currencies and their minimum payout amounts
        self.supported_currencies = {
            CryptoCurrency.BITCOIN: {'min_payout': 0.001, 'network_fee': 0.0005},
            CryptoCurrency.ETHEREUM: {'min_payout': 0.01, 'network_fee': 0.005},
            CryptoCurrency.LITECOIN: {'min_payout': 0.1, 'network_fee': 0.01},
            CryptoCurrency.DOGECOIN: {'min_payout': 10, 'network_fee': 1},
            CryptoCurrency.USDT: {'min_payout': 10, 'network_fee': 5},
            CryptoCurrency.USDC: {'min_payout': 10, 'network_fee': 5}
        }
    
    def _generate_signature(self, payload: str, timestamp: str) -> str:
        """Generate HMAC signature for API authentication"""
        message = f"{timestamp}{payload}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, method: str = "POST", data: Dict = None) -> Dict:
        """Make authenticated request to the payment gateway API"""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))
        payload = json.dumps(data) if data else ""
        signature = self._generate_signature(payload, timestamp)
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
        
        # Mock response for demonstration
        if self.sandbox:
            return self._mock_api_response(endpoint, data)
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, data=payload, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}
    
    def _mock_api_response(self, endpoint: str, data: Dict = None) -> Dict:
        """Mock API responses for demonstration purposes"""
        if endpoint == "/payouts":
            return {
                'success': True,
                'transaction_id': f"tx_{int(time.time())}_{hash(str(data)) % 10000}",
                'status': 'pending',
                'estimated_confirmation_time': '10-30 minutes',
                'network_fee': self.supported_currencies.get(
                    CryptoCurrency(data.get('currency', 'BTC')), {}
                ).get('network_fee', 0.001),
                'gateway_fee': 0.001,  # 0.1% gateway fee
                'created_at': datetime.utcnow().isoformat()
            }
        elif endpoint.startswith("/payouts/"):
            transaction_id = endpoint.split("/")[-1]
            # Simulate different statuses based on transaction ID
            status_map = {
                0: 'pending',
                1: 'processing', 
                2: 'completed',
                3: 'failed'
            }
            status_index = hash(transaction_id) % 4
            status = status_map[status_index]
            
            response = {
                'success': True,
                'transaction_id': transaction_id,
                'status': status,
                'confirmations': 6 if status == 'completed' else 0,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if status == 'completed':
                response['transaction_hash'] = f"0x{hashlib.sha256(transaction_id.encode()).hexdigest()}"
                response['block_number'] = 18500000 + (hash(transaction_id) % 1000)
            elif status == 'failed':
                response['error_message'] = "Insufficient funds in gateway wallet"
            
            return response
        elif endpoint == "/balance":
            return {
                'success': True,
                'balances': {
                    'BTC': 10.5,
                    'ETH': 150.2,
                    'LTC': 500.0,
                    'DOGE': 10000.0,
                    'USDT': 50000.0,
                    'USDC': 45000.0
                }
            }
        elif endpoint == "/rates":
            return {
                'success': True,
                'rates': {
                    'BTC': 45000.00,
                    'ETH': 3000.00,
                    'LTC': 100.00,
                    'DOGE': 0.08,
                    'USDT': 1.00,
                    'USDC': 1.00
                },
                'updated_at': datetime.utcnow().isoformat()
            }
        
        return {'success': False, 'error': 'Unknown endpoint'}
    
    def validate_wallet_address(self, address: str, currency: CryptoCurrency) -> bool:
        """Validate cryptocurrency wallet address format"""
        # Basic validation - in production, use proper address validation libraries
        validation_rules = {
            CryptoCurrency.BITCOIN: lambda addr: addr.startswith(('1', '3', 'bc1')) and len(addr) >= 26,
            CryptoCurrency.ETHEREUM: lambda addr: addr.startswith('0x') and len(addr) == 42,
            CryptoCurrency.LITECOIN: lambda addr: addr.startswith(('L', 'M', 'ltc1')) and len(addr) >= 26,
            CryptoCurrency.DOGECOIN: lambda addr: addr.startswith('D') and len(addr) >= 27,
            CryptoCurrency.USDT: lambda addr: addr.startswith('0x') and len(addr) == 42,  # ERC-20
            CryptoCurrency.USDC: lambda addr: addr.startswith('0x') and len(addr) == 42   # ERC-20
        }
        
        validator = validation_rules.get(currency)
        return validator(address) if validator else False
    
    def get_minimum_payout(self, currency: CryptoCurrency) -> float:
        """Get minimum payout amount for a currency"""
        return self.supported_currencies.get(currency, {}).get('min_payout', 0.001)
    
    def get_network_fee(self, currency: CryptoCurrency) -> float:
        """Get estimated network fee for a currency"""
        return self.supported_currencies.get(currency, {}).get('network_fee', 0.001)
    
    def create_payout(self, wallet_address: str, amount: float, currency: CryptoCurrency, 
                     reference: str = None) -> Dict:
        """Create a payout transaction"""
        # Validate inputs
        if not self.validate_wallet_address(wallet_address, currency):
            return {'success': False, 'error': 'Invalid wallet address'}
        
        min_payout = self.get_minimum_payout(currency)
        if amount < min_payout:
            return {'success': False, 'error': f'Amount below minimum payout of {min_payout} {currency.value}'}
        
        # Prepare payout data
        payout_data = {
            'wallet_address': wallet_address,
            'amount': amount,
            'currency': currency.value,
            'reference': reference or f"payout_{int(time.time())}"
        }
        
        # Make API request
        response = self._make_request("/payouts", "POST", payout_data)
        return response
    
    def get_payout_status(self, transaction_id: str) -> Dict:
        """Get the status of a payout transaction"""
        response = self._make_request(f"/payouts/{transaction_id}", "GET")
        return response
    
    def get_gateway_balance(self) -> Dict:
        """Get gateway wallet balances"""
        response = self._make_request("/balance", "GET")
        return response
    
    def get_exchange_rates(self) -> Dict:
        """Get current cryptocurrency exchange rates"""
        response = self._make_request("/rates", "GET")
        return response
    
    def calculate_payout_fees(self, amount: float, currency: CryptoCurrency) -> Dict:
        """Calculate total fees for a payout"""
        network_fee = self.get_network_fee(currency)
        gateway_fee = amount * 0.001  # 0.1% gateway fee
        total_fee = network_fee + gateway_fee
        net_amount = amount - total_fee
        
        return {
            'gross_amount': amount,
            'network_fee': network_fee,
            'gateway_fee': gateway_fee,
            'total_fee': total_fee,
            'net_amount': max(0, net_amount)
        }
    
    def is_currency_supported(self, currency: CryptoCurrency) -> bool:
        """Check if a currency is supported for payouts"""
        return currency in self.supported_currencies
