#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


import requests
import re
url = 'https://m.weibo.cn/api/comments/show?id=4467107636950632&page=1'
headers = {'Cookies':'your cookie',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
clean = re.compile('<.*?>')
last_id = ''

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    global last_id
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(0.5)
        count += 1
        line=''
        try:
            j = requests.get(url, headers=headers).json()
            print(1)
            latest_comment = j['data']['data'][0]
            latest_id = latest_comment['id']
            print(latest_id,last_id)
            if (latest_id != last_id):
                last_id = latest_id
                comment_text = re.sub(clean, '', latest_comment['text'])
                comment_user = re.sub(clean, '', latest_comment['user']['screen_name'])
                print(comment_text + '   [' + comment_user + '] ')
                line=comment_text + '   [' + comment_user + '] '
            else:
                continue
        except:
            continue

        print(line)

        socketio.emit('my_response',
                      {'data': line, 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


# @socketio.event
# def my_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']})


# @socketio.event
# def my_broadcast_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)


# @socketio.event
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.event
# def leave(message):
#     leave_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('close_room')
# def on_close_room(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                          'count': session['receive_count']},
#          to=message['room'])
#     close_room(message['room'])


# @socketio.event
# def my_room_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          to=message['room'])


# @socketio.event
# def disconnect_request():
#     @copy_current_request_context
#     def can_disconnect():
#         disconnect()

#     session['receive_count'] = session.get('receive_count', 0) + 1
#     # for this emit we use a callback function
#     # when the callback function is invoked we know that the message has been
#     # received and it is safe to disconnect
#     emit('my_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']},
#          callback=can_disconnect)


# @socketio.event
# def my_ping():
#     emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, port=5000,host='0.0.0.0',debug=True)
