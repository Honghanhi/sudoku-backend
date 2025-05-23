from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

rooms = {}  # {roomId: {players: [...], gameStarted: False, ...}}

# Tạo phòng
@app.route('/create-room', methods=['POST'])
def create_room():
    data = request.get_json()
    player_name = data['playerName']
    room_id = str(uuid.uuid4())[:6].upper()
    size = 9
    grid = [[0] * size for _ in range(size)]
    rooms[room_id] = {
        'players': [{'name': player_name, 'ready': False, 'solved': False, 'time': 0}],
        'host': player_name,
        'gameStarted': False,
        'gameFinished': False,
        'grid': grid,
        'size': size,
        'result': {}
    }
    return jsonify({'roomCode': room_id})

# Tham gia phòng
@app.route('/join-room', methods=['POST'])
def join_room():
    data = request.get_json()
    room_id = data['roomId']
    player_name = data['playerName']

    if room_id not in rooms or len(rooms[room_id]['players']) >= 2:
        return 'Room full or does not exist', 400

    rooms[room_id]['players'].append({'name': player_name, 'ready': False, 'solved': False, 'time': 0})
    return jsonify({'hostName': rooms[room_id]['host']})

# Polling trạng thái phòng
@app.route('/room-status/<room_id>', methods=['GET'])
def room_status(room_id):
    if room_id not in rooms:
        return 'Room not found', 404
    return jsonify(rooms[room_id])

# Toggle sẵn sàng
@app.route('/toggle-ready', methods=['POST'])
def toggle_ready():
    data = request.get_json()
    room = rooms.get(data['roomId'])
    if not room:
        return 'Room not found', 404

    for player in room['players']:
        if player['name'] == data['playerName']:
            player['ready'] = data['isReady']

    # Tự động bắt đầu nếu đủ 2 người và đều sẵn sàng
    players = room['players']
    if len(players) == 2 and all(p['ready'] for p in players):
        room['gameStarted'] = True

    return '', 204

# Bắt đầu trận
@app.route('/start-game', methods=['POST'])
def start_game():
    data = request.get_json()
    room = rooms.get(data['roomId'])

    if not room:
        return 'Room not found', 404

    players = room.get('players', [])
    if len(players) != 2:
        return 'Game requires exactly 2 players', 400

    if not all(p.get('ready', False) for p in players):
        not_ready = [p['name'] for p in players if not p.get('ready', False)]
        return jsonify({'error': 'All players must be ready', 'notReady': not_ready}), 400

    room['gameStarted'] = True
    room['grid'] = data['grid']
    room['size'] = data['size']
    return '', 204

# Người chơi hoàn thành
@app.route('/player-finish', methods=['POST'])
def player_finish():
    data = request.get_json()
    room = rooms.get(data['roomId'])
    if not room:
        return 'Room not found', 404
    for player in room['players']:
        if player['name'] == data['playerName']:
            player['solved'] = True
            player['time'] = data['time']
    return '', 204

# Hoàn tất trận đấu
@app.route('/game-complete', methods=['POST'])
def game_complete():
    data = request.get_json()
    room = rooms.get(data['roomId'])
    if not room:
        return 'Room not found', 404
    room['result'] = data['result']
    room['gameFinished'] = True
    return '', 204

# Rời phòng
@app.route('/leave-room', methods=['POST'])
def leave_room():
    data = request.get_json()
    room = rooms.get(data['roomId'])
    if room:
        room['players'] = [p for p in room['players'] if p['name'] != data['playerName']]
        if not room['players']:
            rooms.pop(data['roomId'], None)
    return '', 204

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # lấy PORT từ môi trường, fallback là 5000
    app.run(host='0.0.0.0', port=port)
