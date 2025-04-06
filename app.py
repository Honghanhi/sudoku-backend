from flask import Flask, jsonify
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)  # Cho phép gọi từ frontend khác miền

rooms = set()

@app.route('/create-room', methods=['GET'])
def create_room():
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while room_code in rooms:
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    rooms.add(room_code)
    return jsonify({"room": room_code})
