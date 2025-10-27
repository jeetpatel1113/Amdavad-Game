# Amdavad Board Game

A real-time multiplayer board game implementation of Amdavad, a traditional game from Ahmedabad (Amdavad), India. This digital version brings the classic board game to life using modern web technologies.

🎮 **Play Now**: [https://amdavad-game.onrender.com/](https://amdavad-game.onrender.com/)

## Features

- Real-time multiplayer gameplay
- Interactive game board with drag-and-drop tokens
- Dice rolling system with black and white dice
- Move history tracking
- Score tracking
- Mobile-friendly touch support
- Cross-browser compatibility

## Requirements

- Python 3.6+
- Flask
- Flask-SocketIO
- Flask-CORS
- eventlet

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jeetpatel1113/Amdavad-Game.git
cd Amdavad-Game
```

2. Install the required packages:
```bash
pip install flask flask-socketio flask-cors eventlet
```

## Running the Game

1. Start the server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5555
```

## How to Play

1. The game board consists of a 5x5 grid with X marks in a cross pattern
2. Each player has colored tokens (red, blue, green, yellow)
3. Click on any die to roll all four dice
4. White dice count determines how many moves you can make
5. Drag and drop tokens to move them on the board
6. Special rule: If all dice are black, you get 8 moves

## Game Rules

- Players take turns rolling dice and moving tokens
- The number of white dice determines the number of moves available
- If all dice are black, the player gets 8 moves
- Tokens can be moved to any valid position on the board
- The game keeps track of total moves and dice roll history

## Technical Details

- Frontend: HTML5, CSS3, JavaScript with Canvas API
- Backend: Python Flask with Socket.IO
- Real-time updates using WebSocket communication
- State management handled on the server side
- Responsive design for both desktop and mobile devices

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[MIT License](LICENSE)
