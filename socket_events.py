# Add this file to your project to handle Socket.IO events
from flask_socketio import emit, join_room, leave_room
from app import socketio

# Dictionary to track typing users in each room
typing_users = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    """User joins a specific message room"""
    if 'message_id' not in data:
        return
    
    room = f"message_{data['message_id']}"
    join_room(room)
    print(f"User joined room: {room}")

@socketio.on('leave')
def handle_leave(data):
    """User leaves a specific message room"""
    if 'message_id' not in data:
        return
    
    room = f"message_{data['message_id']}"
    leave_room(room)
    print(f"User left room: {room}")

@socketio.on('typing')
def handle_typing(data):
    """User is typing a message"""
    if 'message_id' not in data or 'user' not in data:
        return
    
    room = f"message_{data['message_id']}"
    user = data['user']
    
    # Track typing user
    if room not in typing_users:
        typing_users[room] = set()
    
    typing_users[room].add(user)
    
    # Broadcast to room
    emit('user_typing', {'user': user}, room=room)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """User stopped typing"""
    if 'message_id' not in data or 'user' not in data:
        return
    
    room = f"message_{data['message_id']}"
    user = data['user']
    
    # Remove user from typing list
    if room in typing_users and user in typing_users[room]:
        typing_users[room].remove(user)
    
    # Broadcast to room
    emit('user_stop_typing', {'user': user}, room=room)

