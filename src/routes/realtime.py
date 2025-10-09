from flask import Blueprint, Response, jsonify, request
import json
import time
import threading
from datetime import datetime
from src.models.mining_data import MiningData
from src.models.profitability import ProfitabilityData
from src.models.ai_models import OptimizationDecision
from src.models.user import db
import random

realtime_bp = Blueprint('realtime', __name__)

# Store active SSE connections
active_connections = set()

class SSEConnection:
    def __init__(self):
        self.queue = []
        self.active = True
    
    def add_event(self, event_type, data):
        if self.active:
            self.queue.append({
                'event': event_type,
                'data': json.dumps(data),
                'timestamp': datetime.now().isoformat()
            })
    
    def get_events(self):
        events = self.queue.copy()
        self.queue.clear()
        return events
    
    def close(self):
        self.active = False

def broadcast_event(event_type, data):
    """Broadcast an event to all active SSE connections"""
    for connection in list(active_connections):
        if connection.active:
            connection.add_event(event_type, data)
        else:
            active_connections.discard(connection)

def generate_mining_data():
    """Generate realistic mining data for demonstration"""
    return {
        'hashrate': round(random.uniform(900, 1100), 2),
        'power': round(random.uniform(1000, 1200), 2),
        'temperature': round(random.uniform(60, 75), 2),
        'profitability': round(random.uniform(0.04, 0.06), 4),
        'efficiency': round(random.uniform(0.8, 1.2), 3),
        'timestamp': datetime.now().isoformat()
    }

def generate_ai_decision():
    """Generate AI optimization decision for demonstration"""
    actions = ['continue_mining', 'switch_coin', 'adjust_power', 'optimize_timing']
    coins = ['BTC', 'ETH', 'LTC', 'DOGE']
    
    return {
        'action': random.choice(actions),
        'target_coin': random.choice(coins),
        'confidence': round(random.uniform(0.7, 0.95), 2),
        'reason': f"Market conditions favor {random.choice(['efficiency', 'profitability', 'stability'])} optimization",
        'expected_improvement': f"{random.randint(3, 15)}% efficiency gain",
        'timestamp': datetime.now().isoformat()
    }

def generate_profitability_update():
    """Generate profitability update for demonstration"""
    return {
        'daily_profit': round(random.uniform(0.045, 0.065), 4),
        'weekly_trend': round(random.uniform(-5, 15), 2),
        'roi_percentage': round(random.uniform(8, 25), 2),
        'market_score': round(random.uniform(0.6, 0.9), 2),
        'timestamp': datetime.now().isoformat()
    }

def data_generator():
    """Background thread to generate and broadcast real-time data"""
    while True:
        try:
            # Generate mining data every 2 seconds
            mining_data = generate_mining_data()
            broadcast_event('mining_update', mining_data)
            
            # Generate AI decision every 10 seconds
            if int(time.time()) % 10 == 0:
                ai_decision = generate_ai_decision()
                broadcast_event('ai_decision', ai_decision)
            
            # Generate profitability update every 15 seconds
            if int(time.time()) % 15 == 0:
                profitability_data = generate_profitability_update()
                broadcast_event('profitability_update', profitability_data)
            
            time.sleep(2)
        except Exception as e:
            print(f"Error in data generator: {e}")
            time.sleep(5)

# Start background data generator
data_thread = threading.Thread(target=data_generator, daemon=True)
data_thread.start()

@realtime_bp.route('/stream')
def stream():
    """SSE endpoint for real-time data streaming"""
    def event_stream():
        connection = SSEConnection()
        active_connections.add(connection)
        
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Real-time stream connected'})}\n\n"
            
            while connection.active:
                events = connection.get_events()
                for event in events:
                    yield f"event: {event['event']}\n"
                    yield f"data: {event['data']}\n\n"
                
                time.sleep(0.5)  # Check for new events every 500ms
                
        except GeneratorExit:
            connection.close()
            active_connections.discard(connection)
        except Exception as e:
            print(f"SSE stream error: {e}")
            connection.close()
            active_connections.discard(connection)
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@realtime_bp.route('/status')
def stream_status():
    """Get current stream status and active connections"""
    return jsonify({
        'active_connections': len(active_connections),
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@realtime_bp.route('/trigger/<event_type>')
def trigger_event(event_type):
    """Manually trigger an event for testing purposes"""
    if event_type == 'mining':
        data = generate_mining_data()
        broadcast_event('mining_update', data)
    elif event_type == 'ai':
        data = generate_ai_decision()
        broadcast_event('ai_decision', data)
    elif event_type == 'profitability':
        data = generate_profitability_update()
        broadcast_event('profitability_update', data)
    else:
        return jsonify({'error': 'Invalid event type'}), 400
    
    return jsonify({
        'message': f'Event {event_type} triggered successfully',
        'data': data
    })
