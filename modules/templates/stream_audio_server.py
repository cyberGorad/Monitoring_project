from flask import Flask, Response
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

def generate_audio():
    while True:
        yield b'audio-data'

@app.route('/stream')
def stream():
    return Response(generate_audio(), mimetype="audio/mpeg")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
