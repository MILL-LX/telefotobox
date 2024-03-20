import time
import pigpio
import subprocess
import json
import socketio

# ------------------------------------------------------------------------------

PI_HIGH = 1
PI_LOW = 0

# ------------------------------------------------------------------------------
# setup socket connection to nodejs server
# ------------------------------------------------------------------------------

sio = socketio.Client()

SERVER = 'http://localhost:8000'

@sio.event
def connect():
    print('connection established')
    time.sleep(3)
    sio.emit('dialer_ready')

@sio.event
def disconnect():
    print('disconnected from server')

# ------------------------------------------------------------------------------
# Pin assignment. Note that the pin numbers should be those mentioned in the
# Broadcom. In the comments the corresponding GPIO pin on the connector. For
# better understanding, the pin global constants are ordered by connector pin
# number.
# ------------------------------------------------------------------------------
pin_dial_counter = 17       # Count the dialed number (pin 11)
pin_dial_detect = 22        # Detect number dialing (pin 13)

pin_hook = 10               # Detect number dialing (pin 13)

# ------------------------------------------------------------------------------
# Global variables, flags and counters
# ------------------------------------------------------------------------------

cb_dialer_handler = 0       # Callback handler for the rotary dialer
cb_counter_handler = 0      # Callback handler for the rotary pulse counter

# Initially set to false it is True when the user start dialing a number with the
# rotary dialer. The status remain True until the rotary dialer has not completed the
# counterclockwise rotation emitting all the impulses corresponding to the dialled
# number.
dialer_status = False   # Become true when the user start dialing a number

# Pulse counter of the rotary dialer. WHen the dialer_status is high the
# counter is incrememnted while, when the dialer_status goes low the dialed
# number sequence is updated with the last number dialed.
pulses = 0

# Compound dialed number in string format. Until a number is not recognized as a command
# the further dialed numbers are queued to the string. It the number of characters of the
# dialed number reach the max lenght and has no meaning the number is reset and the counter
# restart to a new number.
dialed_number = ''

# Maximum number of characters of the dialed number.
# This depends on the numeric commands structures decided by the program. A three-number
# command code is sufficient for 999 different commands, maybe sufficient!
max_numbers = 4

# PiGPIO library instance, globally defined
pi = pigpio.pi()

print("get_hardware_revision() => ", pi.get_hardware_revision())

pi.set_glitch_filter(pin_dial_detect, 250)
pi.set_glitch_filter(pin_dial_counter, 100)
pi.set_glitch_filter(pin_hook, 250)


def initGPIO():
    '''
    Initialize the GPIO library and set the callback for the interested
    pins with the corresponding function.
    Note that the Broadcom GPIO pin 28 should not be set to a callback
    to avoid problems.
    '''

    global pi

    print('initGPIO()')

    # Set the input pins
    pi.set_mode(pin_dial_counter, pigpio.INPUT)
    pi.set_pull_up_down(pin_dial_counter, pigpio.PUD_DOWN)
    pi.set_mode(pin_dial_detect, pigpio.INPUT)
    pi.set_pull_up_down(pin_dial_detect, pigpio.PUD_DOWN)
    pi.set_mode(pin_hook, pigpio.INPUT)
    pi.set_pull_up_down(pin_hook, pigpio.PUD_DOWN)

    # Set the callback for the interested pins and gets the handlers
    set_callbacks()

    reinit()


def set_callbacks():
    '''
    Enable the callback functions associated to the GPIO pins
    and save the callback handlers
    '''
    global pi
    global cb_counter_handler
    global cb_dialer_handler

    print('set_callbacks()')

    cb_dialer_handler = pi.callback(
        pin_hook, pigpio.EITHER_EDGE, hook_detect)
    cb_dialer_handler = pi.callback(
        pin_dial_detect, pigpio.EITHER_EDGE, dial_detect)
    cb_counter_handler = pi.callback(
        pin_dial_counter, pigpio.EITHER_EDGE, pulse_count)


def hook_detect(self, event, tick):
    global hook_status
    global pi
    hook_status = pi.read(pin_hook)
    print('hook_detect()', hook_status)
    sio.emit('hook', hook_status)


def dial_detect(self, event, tick):
    '''
    Manage the dialer pulses to encode the dialed number
    then the number is queued to the string collecting the numbers
    processed by the main program.
    The dialer works only if the pick up is open.
    '''
    global dialer_status
    global pulses
    global max_numbers
    global dialed_number
    global pi

    print('dial_detect()')

    dialer_status = pi.read(pin_dial_detect)

    # Check if a number is to be dialed
    if dialer_status is PI_HIGH:
        # Reset the pulses counter
        print('dialer_status is PI_HIGH')
        pulses = 0

    # Check if the dialed number has reached the maximum length
    # to reset the number and start a new queue
    if len(dialed_number) >= max_numbers:
        dialed_number = ''      # Reset the number sequence
    else:
        # Queue the dialed number
        if pulses != 0:
            # When the cipher 0 is dialed the rotary wheel
            # emit 22 pulses!!!
            # então consideramos que são 3 e dividido por 2 = 1,5 e a isso subtraído 1 e arredondado...
            # dá 0 !!!!!!!!!!!!!! cenas.
            if pulses == 22:
                pulses = 3

            # maradice para conseguir ler o número certo...
            numero_marcado = int(pulses / 2) - 1

            # e finalmente fica o que queremos como global!
            dialed_number = dialed_number + str(numero_marcado)
            # Check if the user has dialed a valid number associated to
            # a command.
            print('acreditamos que o número é o ', numero_marcado)
            # dica = 'acreditamos que o número é o ' + str(numero_marcado)
            # socket.write(channel, dica)
            check_number()


def pulse_count(self, event, tick):
    '''
    Count the pulses when the user dials a number. Only the HIGH values are
    considered as pulses and the counter increase the number only when the
    dialer_status value is HIGH.

    Note that the number of pulses is doubled as the interrupt
    read both the transitions to and from high.
    '''
    global pulses

    if dialer_status is PI_HIGH:
        pulses += 1
        # print("pulses + 1 = ", pulses, " | tick NOW = ", pi.get_current_tick())

        print("pulses + 1 = ", pulses)


def check_number():
    '''
    Check if the current number corresponds to a valid command.
    '''
    global dialed_number
    global pi

    print(str(dialed_number))

    # Numeric commands and related functions
    if dialed_number != '':
        if len(dialed_number) >= max_numbers:

            sio.emit('year', dialed_number)

            if int(dialed_number) == 666:
                # Restart the appplication to initial conditions
                dialed_number = ''
                reinit()


def reinit():
    '''
    Restart the appplication to initial conditions
    '''
    global pi
    global dialed_number

    dialed_number = ''


if __name__ == '__main__':
    # Main application

    initGPIO()

    sio.connect(SERVER)
    sio.wait()

    # looping infinitely
    while True:
        pass
