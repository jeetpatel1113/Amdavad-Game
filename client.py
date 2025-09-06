import pygame
import socket
import threading
import pickle

# ---------- SETTINGS ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
GRID_SIZE = 5
CELL_SIZE = 100

rack_x = WIDTH - 180
rack_y = 70

colors = {
    'red': (255, 0, 0), 'blue': (0, 0, 255),
    'green': (0, 255, 0), 'yellow': (255, 255, 0),
    'white': (255, 255, 255), 'black': (0, 0, 0),
    'grid': (50, 50, 50)
}

# ---------- NETWORK ----------
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5000))

tokens = []
dice = ['white'] * 4
roll_history = []

def recv_data():
    global tokens, dice, roll_history
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            obj = pickle.loads(data)
            if obj.get('type') == 'updateTokens':
                tokens = obj['tokens']
            elif obj.get('type') == 'dice':
                dice = obj['dice']
                roll_history = obj['history']
            elif obj.get('type') == 'init':
                tokens = obj['tokens']
                dice = obj['dice']
                roll_history = obj['history']
        except:
            break

threading.Thread(target=recv_data, daemon=True).start()

# ---------- PYGAME ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Board Game Client")
clock = pygame.time.Clock()
dragging = None

# ---------- DRAW HELPERS ----------
def draw_grid():
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, colors['grid'],
                         (i * CELL_SIZE, 0), (i * CELL_SIZE, GRID_SIZE * CELL_SIZE), 2)
        pygame.draw.line(screen, colors['grid'],
                         (0, i * CELL_SIZE), (GRID_SIZE * CELL_SIZE, i * CELL_SIZE), 2)

def draw_crosses():
    positions = [(1, 3), (3, 1), (3, 3), (3, 5), (5, 3)]
    for r, c in positions:
        cx = c * CELL_SIZE - CELL_SIZE // 2
        cy = r * CELL_SIZE - CELL_SIZE // 2
        offset = CELL_SIZE // 2 - 8
        pygame.draw.line(screen, (0, 0, 0), (cx - offset, cy - offset), (cx + offset, cy + offset), 6)
        pygame.draw.line(screen, (0, 0, 0), (cx - offset, cy + offset), (cx + offset, cy - offset), 6)

def draw_tokens():
    TOKEN_RADIUS = 12
    for t in tokens:
        color = colors[t['color']]
        if t == dragging:
            pygame.draw.circle(screen, colors['black'], (t['x'], t['y']), TOKEN_RADIUS + 2, width=2)
        pygame.draw.circle(screen, color, (t['x'], t['y']), TOKEN_RADIUS)

def draw_dice():
    for i, color in enumerate(dice):
        rect = pygame.Rect(150 + i * 70, HEIGHT - 100, 60, 60)
        pygame.draw.rect(screen, colors[color], rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)

def draw_roll_history():
    font = pygame.font.SysFont(None, 24)
    start_x = WIDTH - 200
    y = 50
    label = font.render("Last 5 Rolls:", True, (0, 0, 0))
    screen.blit(label, (start_x, y))
    y += 30
    for entry in reversed(roll_history):
        d_str = ''.join(['W' if f == 'white' else 'B' for f in entry['dice']])
        text = font.render(f"{d_str} → {entry['score']}", True, (0, 0, 0))
        screen.blit(text, (start_x, y))
        y += 25

def draw_board():
    screen.fill((200, 200, 200))
    draw_grid()
    draw_crosses()
    draw_tokens()
    draw_dice()
    draw_roll_history()

# ---------- MAIN LOOP ----------
running = True
while running:
    clock.tick(FPS)
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # check token grab
            for t in reversed(tokens):
                if (mx - t['x']) ** 2 + (my - t['y']) ** 2 <= 20 ** 2:
                    dragging = t
                    break
            # check dice click
            for i in range(4):
                x, y, w, h = 150 + i * 70, HEIGHT - 100, 60, 60
                if x < mx < x + w and y < my < y + h:
                    client.sendall(pickle.dumps({'type': 'roll'}))

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                dragging = None
                client.sendall(pickle.dumps({'type': 'move', 'tokens': tokens}))

        elif event.type == pygame.MOUSEMOTION and dragging:
            dragging['x'], dragging['y'] = event.pos

pygame.quit()
