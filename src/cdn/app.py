import logging
import requests
import os
import sys
import time

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, rooms, leave_room, join_room, close_room


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins=['http://127.0.0.1:5000', 'http://localhost:5000', '*'])

streamers = {}
streams = {}


@app.route("/",methods=["GET"])
def index():
    return "You probably shouldn't be here."


@socketio.on("register_new_stream")
def create_a_new_stream(data):
    logging.info({"message": "new stream registration", "data": data})
    if "streamid" not in data:
        emit("stream_registration_response", {"result": "failure", "reason": "missing field 'streamid'"})
        return

    # HOX TODO: What if we get multiple streams with same name? Even to different servers?
    if data["streamid"] in streams:
        ...

    if request.sid in streamers and streamers[request.sid] != data["streamid"] :
        del streams[data["streamid"]]
        close_room(streams[request.sid])

    streamers[request.sid] = data["streamid"]
    streams[data["streamid"]] = request.sid

    logging.info({"message": "registered a new stream successfully", "streamid": data["streamid"]})
    emit("stream_registration_response", {"result": "success"})


@socketio.on("broadcast_data")
def handle_incoming_data(data):
    logging.info({"message": "received broadcasted data", "length of data": len(data)})
    if request.sid not in streamers:
        emit("data_broadcast_result", {"result": "failure", "reason": "streamer not registered"})
        return

    if "streamid" not in data:
        emit("data_broadcast_result", {"result": "failure", "reason": "missing 'streamid' field"})
        return

    if "data" not in data:
        emit("data_broadcast_result", {"result": "failure", "reason": "missing 'data' field"})
        return

    emit("data_broadcast_result", {"result": "success"})
    emit("streaming_data", data["data"], to=streamers[request.sid])


@socketio.on("watch_stream")
def put_to_room(data):
    if "streamid" not in data:
        emit("stream_request_response", {"result": "failure", "reason": "missing field 'streamid'"})
        return
    
    if data["streamid"] not in streams:
        emit("stream_request_response", {"result": "failure", "reason": "requested stream doesn't exist", "streamid": data["streamid"]})
        return

    for room in rooms():
        leave_room(room)

    emit("stream_request_response", {"result": "success", "stream_event_name": "streaming_data", "streamid": data["streamid"]})
    time.sleep(1)
    join_room(data["streamid"])


if __name__ == '__main__':
    time.sleep(2)  # Give some time for the load balancer to spin up
    requests.post(
        url=f"http://{os.environ['LOAD_BALANCER_HOSTNAME']}:{os.environ['LOAD_BALANCER_PORT']}/register_server",
        json={
            "address": "127.0.0.1",
            "hostname": os.environ["HOSTNAME"],
            "port": os.environ["OUTSIDE_PORT"],
        }
    )
    socketio.run(
        app,
        debug=True,
        port=os.environ["PORT"],
        host=os.environ["ADDRESS"],
        allow_unsafe_werkzeug=True
    )
