import board
import keypad
import socketio
import time

# 1. Configuração do Socket.IO (Cliente)
sio = socketio.Client()

try:
    sio.connect('http://localhost:8000', transports=['websocket'])
    print("Conectado ao servidor Telefotobox via Websocket!")
except Exception as e:
    print(f"Erro ao ligar ao servidor: {e}")

# 2. Configuração do Hardware (Teu script funcional)
ROWS = [board.D16, board.D6, board.D13, board.D19]
COLS = [board.D26, board.D20, board.D21]
keys = keypad.KeyMatrix(ROWS, COLS, interval=0.02)

# Mapeamento do teclado 3x4
KEY_MAP = {
    0: "1", 1: "2", 2: "3",
    3: "4", 4: "5", 5: "6",
    6: "7", 7: "8", 8: "9",
    9: "*", 10: "0", 11: "#"
}

# 3. Variáveis de Controlo
buffer = ""
last_key_time = 0
TIMEOUT = 2.0  # Tempo para enviar automaticamente após parar de digitar

print("Aguardando introdução de ano no Keypad...")

try:
    while True:
        event = keys.events.get()

        if event:
            if event.pressed:
                key_idx = event.key_number
                key_char = KEY_MAP.get(key_idx)

                if key_char:
                    if key_char.isdigit():
                        buffer += key_char
                        last_key_time = time.time()
                        print(f"Buffer atual: {buffer}")
                    
                    elif key_char == "#":
                        # Envio imediato (Enter)
                        if buffer:
                            print(f"Enviando via Socket: {buffer}")
                            sio.emit('year', buffer)
                            buffer = ""
                    
                    elif key_char == "*":
                        # Limpar buffer
                        print("Buffer limpo.")
                        buffer = ""

        # 4. Lógica de Envio Automático (Timeout)
        # Se houver algo no buffer e o utilizador parou de digitar há X segundos
        if buffer != "" and (time.time() - last_key_time) > TIMEOUT:
            print(f"Timeout atingido. Enviando ano: {buffer}")
            sio.emit('year', buffer)
            buffer = ""

        time.sleep(0.01)

except KeyboardInterrupt:
    print("A desligar...")
finally:
    sio.disconnect()