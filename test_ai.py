import board
import keypad
import digitalio
import socketio
import time

# 1. Configuração do Socket.IO (Transmissão para a porta 8000)
sio = socketio.Client()

def connect_socket():
    if not sio.connected:
        try:
            sio.connect('http://localhost:8000', transports=['websocket'])
            print("Conectado ao servidor Telefotobox (Porta 8000)")
        except:
            pass # Tenta novamente no loop se necessário

connect_socket()

# 2. Configuração do Hardware TeleJuke
# Teclado (conforme o teu script funcional)
ROWS = [board.D16, board.D6, board.D13, board.D19]
COLS = [board.D26, board.D20, board.D21]
keys = keypad.KeyMatrix(ROWS, COLS, interval=0.02)

KEY_MAP = {
    0: "1", 1: "2", 2: "3",
    3: "4", 4: "5", 5: "6",
    6: "7", 7: "8", 8: "9",
    9: "*", 10: "0", 11: "#"
}

# Gancho (Hook Switch) - Padrão TeleJuke Hardware
hook = digitalio.DigitalInOut(board.D12)
hook.direction = digitalio.Direction.INPUT
hook.pull = digitalio.Pull.UP

# 3. Variáveis de Estado
buffer = ""
last_key_time = 0
TIMEOUT = 2.0
# No TeleJuke, hook.value = True significa "No Gancho"
# No TeleJuke, hook.value = False significa "Levantado"
is_off_hook = not hook.value 

print(f"Sistema TeleJuke -> Telefotobox Iniciado.")
print(f"Gancho inicial: {'Levantado' if is_off_hook else 'No Gancho'}")

while True:
    # --- GESTÃO DO GANCHO ---
    # hook.value é True (1) quando pousado, False (0) quando levantado
    current_off_hook = hook.value 

    if current_off_hook != is_off_hook:
        is_off_hook = current_off_hook
        if is_off_hook:
            print("Telefone Levantado (OFF HOOK)")
            sio.emit('hook', 0)
        else:
            print("Telefone Pousado (ON HOOK)")
            sio.emit('hook', 1)
            buffer = "" # Limpa tudo ao desligar

    # --- GESTÃO DO TECLADO (Apenas se o telefone estiver levantado) ---
    if is_off_hook:
        event = keys.events.get()
        if event:
            if event.pressed:
                key_char = KEY_MAP.get(event.key_number)
                if key_char:
                    if key_char.isdigit():
                        buffer += key_char
                        last_key_time = time.time()
                        print(f"Buffer: {buffer}")
                    elif key_char == "#":
                        if buffer:
                            print(f"Enviando ano: {buffer}")
                            sio.emit('year', buffer)
                            buffer = ""
                    elif key_char == "*":
                        buffer = ""
                        print("Reset buffer")

        # Envio automático se o utilizador parar de digitar
        if buffer != "" and (time.time() - last_key_time) > TIMEOUT:
            print(f"Enviando ano (timeout): {buffer}")
            sio.emit('year', buffer)
            buffer = ""

    # Pequeno delay para estabilidade
    time.sleep(0.02)
    current_off_hook = hook.value
    
    # Garantir que a ligação socket não caiu
    if not sio.connected and int(time.time()) % 5 == 0:
        connect_socket()