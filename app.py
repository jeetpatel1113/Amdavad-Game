import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os

load_dotenv()  # Load environment variables

SECRET_GAME_PASSWORD = os.getenv("SECRET_GAME_PASSWORD")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Default X-box positions (tokens start here)
X_POSITIONS = [
    (0, 2),  # Top
    (2, 0),  # Left
    (2, 4),  # Right
    (4, 2)   # Bottom
]

def reset_game_state():
    tokens = []
    colors = ['red', 'blue', 'green', 'yellow']
    start_positions = [(50, 50), (200, 50), (350, 50), (500, 50)]  # pixel start, can adjust

    for i, color in enumerate(colors):
        x_grid, y_grid = X_POSITIONS[i]
        # Convert grid to pixel positions (CELL_SIZE=120, radius offset)
        x_pix = x_grid * 120 + 60
        y_pix = y_grid * 120 + 60
        for j in range(4):
            tokens.append({
                'x': x_pix + j*20,  # small offset for multiple tokens
                'y': y_pix,
                'color': color,
                'id': f'{color}-{j}'
            })

    return {
        'tokens': tokens,
        'dice': ['white', 'white', 'white', 'white'],
        'roll_history': [],
        'white_count': 0,
        'move_count': 0
    }

# Initialize game state
game_state = reset_game_state()

# ----------------------
# Routes
# ----------------------

@app.route('/')
def index():
    return render_template('index.html')

# ----------------------
# Socket.IO Handlers
# ----------------------

@socketio.on('connect')
def handle_connect():
    print("Client connected, waiting for auth")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('auth')
def handle_auth(data):
    password = data.get('password')
    if password == SECRET_GAME_PASSWORD:
        emit('auth_result', {'success': True})
        emit('game_state', game_state)
    else:
        emit('auth_result', {'success': False})

@socketio.on('request_state')
def handle_request_state():
    emit('game_state', game_state)

@socketio.on('roll_dice')
def handle_roll_dice():
    game_state['dice'] = [random.choice(['white', 'black']) for _ in range(4)]
    white_count = sum(1 for d in game_state['dice'] if d == 'white')
    if white_count == 0:
        white_count = 8
    game_state['white_count'] = white_count
    game_state['roll_history'].insert(0, {'dice': game_state['dice'].copy(), 'count': white_count})
    game_state['roll_history'] = game_state['roll_history'][:5]
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
    for token in game_state['tokens']:
        if token['id'] == token_id:
            token['x'] = new_x
            token['y'] = new_y
            break
    game_state['move_count'] += 1
    socketio.emit('tokens_updated', {'tokens': game_state['tokens'], 'move_count': game_state['move_count']})

@socketio.on('reset_game')
def handle_reset_game():
    global game_state
    game_state = reset_game_state()
    socketio.emit('game_reset', game_state)

# ----------------------
# Main
# ----------------------

if __name__ == '__main__':
    print("Starting server on port 5555...")
    socketio.run(app, host='0.0.0.0', port=5555)
