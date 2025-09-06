# ---------- server.py ----------
import socket, threading, pickle, random

HOST = "0.0.0.0"
PORT = 5000

clients = []
lock = threading.Lock()

# initial game state
tokens = [{'x': 650 + (i % 4) * 25, 'y': 300 + (i // 4) * 25, 'color': c}
          for c in ['red', 'blue', 'green', 'yellow'] for i in range(4)]
dice = ['black', 'black', 'black', 'black']
roll_history = []

def broadcast(msg):
    dead = []
    data = pickle.dumps(msg)
    with lock:
        for c in clients:
            try:
                c.sendall(data)
            except:
                dead.append(c)
        for d in dead:
            clients.remove(d)

def handle_client(conn, addr):
    global tokens, dice, roll_history
    print(f"client {addr} connected")

    # send snapshot
    snapshot = {'type': 'init', 'tokens': tokens, 'dice': dice, 'history': roll_history}
    conn.sendall(pickle.dumps(snapshot))

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            obj = pickle.loads(data)

            if obj.get('type') == 'roll':
                dice = [random.choice(['white', 'black']) for _ in range(4)]
                score = sum(1 for face in dice if face == 'white')
                # map special 0w4b -> score 8
                if score == 0:
                    score = 8
                roll_history.append({'dice': dice.copy(), 'score': score})
                roll_history = roll_history[-5:]
                broadcast({'type': 'dice', 'dice': dice, 'history': roll_history})

            elif obj.get('type') == 'move':
                tokens = obj['tokens']
                broadcast({'type': 'updateTokens', 'tokens': tokens})

        except Exception as e:
            print("client error", e)
            break

    with lock:
        if conn in clients:
            clients.remove(conn)
    conn.close()
    print(f"client {addr} disconnected")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        with lock:
            clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
