import board 
import keypad
import digitalio

ROWS = [board.D16, board.D6, board.D13, board.D19]
COLS = [board.D26, board.D20, board.D21]

keys = keypad.KeyMatrix(ROWS, COLS, interval = 0.02)


def getKey():
	keyP = None
	while True:
		event = keys.events.get()
		key_1 = keypad.Event(0, pressed = True)
		key_2 = keypad.Event(1, pressed = True)
		key_3 = keypad.Event(2, pressed = True)
		key_4 = keypad.Event(3, pressed = True)
		key_5 = keypad.Event(4, pressed = True)
		key_6 = keypad.Event(5, pressed = True)
		key_7 = keypad.Event(6, pressed = True)
		key_8 = keypad.Event(7, pressed = True)
		key_9 = keypad.Event(8, pressed = True)
		key_ast = keypad.Event(9, pressed = True)
		key_0 = keypad.Event(10, pressed = True)
		key_car = keypad.Event(11, pressed = True)
		
		if event.__eq__(key_1):
			keyP = "1"
		elif event.__eq__(key_2):
			keyP = "2"
		elif event.__eq__(key_3):
			keyP = "3"
		elif event.__eq__(key_4):
			keyP = "4"
		elif event.__eq__(key_5):
			keyP = "5"
		elif event.__eq__(key_6):
			keyP = "6"
		elif event.__eq__(key_7):
			keyP = "7"
		elif event.__eq__(key_8):
			keyP = "8"
		elif event.__eq__(key_9):
			keyP = "9"
		elif event.__eq__(key_ast):
			keyP = "*"
		elif event.__eq__(key_0):
			keyP = "0"
		elif event.__eq__(key_car):
			keyP = "#"
		else:
			keyP = None
			
		if not (event is None) and not(keyP is None):
			print (f'Key pressed:', keyP)
			return keyP
		
while True:
	KeyLucky = getKey()
	print (KeyLucky)
	
