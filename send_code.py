import socketio

# standard Python
with socketio.SimpleClient() as sio:
    # ... connect to a server and use the client
    # ... no need to manually disconnect!
    sio = socketio.Client()

    sio.connect('http://localhost:8000', transports=['websocket'])


    sio.emit('year', "2019")
    sio.wait()


# if __name__ == '__main__':
#     # Main application

#     sio.connect(SERVER)
#     sio.wait()

#     sio.emit('year', 2020)

#     # looping infinitely
#     while True:
#         pass