import logging
import sys
import time

from flask import Flask, request, redirect, url_for
from flask_socketio import SocketIO, emit, rooms, leave_room, join_room, close_room

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

IP = "127.0.0.1"
IP = "0.0.0.0"  # Comment this out if you run this server outside docker

app = Flask("Server node flask")
socketio = SocketIO(app)
content_storage = {} 

streamers = {}
streams = {}

""" Broadcaster related routes """

@socketio.on('broadcast_connect')
def handle_new_broadcaster():
    logging.info({"message": "received new broadcast connection through socketio"})


@socketio.on("register_new_stream")
def create_a_new_stream(data):
    logging.info({"message": "new stream registration", "data": data})
    if "stream_name" not in data:
        emit("stream_registration_response", {"result": "failure", "reason": "missing field 'stream_name'"})
        return

    if request.sid in streamers and streamers[request.sid] != data["stream_name"] :
        del streams[data["stream_name"]]
        close_room(streams[request.sid])
        
    streamers[request.sid] = data["stream_name"]
    streams[data["stream_name"]] = request.sid
    logging.info({"message": "registered a new stream successfully", "stream_name": data["stream_name"]})
    emit("stream_registration_response", {"result": "success"})


@socketio.on("broadcast_data")
def handle_incoming_data(data):
    logging.info({"message": "received broadcasted data", "payload": data})
    if request.sid not in streamers:
        emit("data_broadcast_result", {"result": "failure", "reason": "streamer not registered"})
        return
    emit("data_broadcast_result", {"result": "success"})
    emit("streaming_data", data, to=streamers[request.sid])


""" Consumer related routes """

@app.route("/")
def show_help():
    return redirect(url_for("show_streams"))


@app.get("/streams")
def show_streams():
    return {"streams": [key for key in streams.keys()]}


@socketio.on("watch_stream")
def put_to_room(data):
    if "stream_name" not in data:
        emit("stream_request_response", {"result": "failure", "reason": "missing field 'stream_name'"})
        return
    
    if data["stream_name"] not in streams:
        emit("stream_request_response", {"result": "failure", "reason": "requested stream doesn't exist", "stream_name": data["stream_name"]})
        return

    for room in rooms():
        leave_room(room)

    emit("stream_request_response", {"result": "success", "stream_event_name": "streaming_data", "stream_name": data["stream_name"]})
    time.sleep(1)
    join_room(data["stream_name"])


if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host=IP, allow_unsafe_werkzeug=True)