import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import os

# ======================
# Config & Globals
# ======================

SECRET_GAME_PASSWORD = "jeetmaster"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Game state (server is the single source of truth)
game_state = {
    'tokens': [
        {'x': 50 + (i % 4) * 30, 'y': 560, 'color': 'red', 'id': f'red-{i}'} for i in range(4)
    ] + [
        {'x': 200 + (i % 4) * 30, 'y': 560, 'color': 'blue', 'id': f'blue-{i}'} for i in range(4)
    ] + [
        {'x': 350 + (i % 4) * 30, 'y': 560, 'color': 'green', 'id': f'green-{i}'} for i in range(4)
    ] + [
        {'x': 500 + (i % 4) * 30, 'y': 560, 'color': 'yellow', 'id': f'yellow-{i}'} for i in range(4)
    ],
    'dice': ['white', 'white', 'white', 'white'],
    'roll_history': [],
    'white_count': 0,
    'move_count': 0
}

# ======================
# Routes
# ======================

@app.route('/')
def index():
    return render_template('index.html')

# ======================
# Socket.IO Event Handlers
# ======================

@socketio.on('connect')
def handle_connect():
    print(f"Client connected, waiting for auth")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('auth')
def handle_auth(data):
    password = data.get('password')
    if password == SECRET_GAME_PASSWORD:
        emit('auth_result', {'success': True})
        # Immediately send full game state after successful auth
        emit('game_state', game_state)
    else:
        emit('auth_result', {'success': False})

@socketio.on('request_state')
def handle_request_state():
    emit('game_state', game_state)

@socketio.on('roll_dice')
def handle_roll_dice():
    # Roll 4 dice (white/black)
    game_state['dice'] = [random.choice(['white', 'black']) for _ in range(4)]
    white_count = sum(1 for d in game_state['dice'] if d == 'white')
    
    # Special rule: 0 white = 8
    if white_count == 0:
        white_count = 8
    
    game_state['white_count'] = white_count
    
    # Update roll history
    game_state['roll_history'].insert(0, {
        'dice': game_state['dice'].copy(),
        'count': white_count
    })
    game_state['roll_history'] = game_state['roll_history'][:5]  # Keep last 5 rolls
    
    # Broadcast to all clients
    socketio.emit('dice_rolled', {
        'dice': game_state['dice'],
        'white_count': white_count,
        'roll_history': game_state['roll_history']
    })

@socketio.on('move_token')
def handle_move_token(data):
    token_id = data.get('token_id')
    new_x = data.get('x')
    new_y = data.get('y')
    
    # Update token position in game state
    for token in game_state['tokens']:
        if token['id'] == token_id:
            token['x'] = new_x
            token['y'] = new_y
            break
    
    game_state['move_count'] += 1
    
    # Broadcast updated token positions
    socketio.emit('tokens_updated', {
        'tokens': game_state['tokens'],
        'move_count': game_state['move_count']
    })

# ======================
# Main
# ======================

if __name__ == '__main__':
    print("Starting server on port 5555...")
    socketio.run(app, host='0.0.0.0', port=5555)
