from flask import Flask, render_template, request,redirect,url_for,logging
from flask_socketio import SocketIO, join_room, leave_room
import gevent
import eventlet
import requests
import random
app = Flask(__name__)
socketio = SocketIO(app)

user_online = []

@app.route('/')
def main():
    num = random.randint(0,1642)
    api_url = "https://type.fit/api/quotes"
    r = requests.get(api_url)
    json = r.json()
    quote = json[num]['text']
    author = json[num]['author']
    number = 0
    for i in user_online:
        number = number +1
    
  
    return render_template("homepage.html",quote=quote,author=author,number=number)

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username,room=room)
    else:
        return redirect(url_for('main'))
    


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    
    username = request.args.get('username')
    
    if username != data['username']:
        socketio.emit('receive_message', data, room=data['room'])
    else:
        socketio.emit('receive_selfmessage',room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)
    user_online.append(data['username'])
    


    
@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])
    user_online.remove(data['username'])
  


if __name__ == '__main__':
    socketio.run(app, host = '127.0.0.1', debug=True)