import logging
import os
import sys
import time
import requests

from flask import Flask, request, redirect, url_for
from flask_socketio import SocketIO, emit, rooms, leave_room, join_room, close_room

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

LOCAL_TESTING_IP = "127.0.0.1"
LOCAL_TESTING_HOSTNAME = "the_only_server"
LOCAL_TESTING_PORT = 10001

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

    # HOX TODO: What if we get multiple streams with same name? Even to different servers?
    if data["stream_name"] in streams:
        ...

    if request.sid in streamers and streamers[request.sid] != data["stream_name"] :
        del streams[data["stream_name"]]
        close_room(streams[request.sid])
    
    response = requests.post(f"http://{os.environ['LOAD_BALANCER_HOSTNAME']}:{os.environ['LOAD_BALANCER_PORT']}/register_new_stream",
                             json={
                                 "stream_name": data["stream_name"],
                                 "hostname": os.environ.get("HOSTNAME", LOCAL_TESTING_HOSTNAME),
                             }
                             )

    if response.status_code != 200:
        logging.warning({"message": "registering a stream to load balancer failed", "stream name": data["stream_name"]})
        emit("stream_registration_response", {"result": "failure", "reason": "couldn't register the stream"})
        return


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
    time.sleep(2)
    requests.post(
        url=f"http://{os.environ['LOAD_BALANCER_HOSTNAME']}:{os.environ['LOAD_BALANCER_PORT']}/register_server",
        json={
            "address": os.environ.get("ADDRESS", LOCAL_TESTING_IP),
            "hostname": os.environ.get("HOSTNAME", LOCAL_TESTING_HOSTNAME),
            "port": os.environ.get("PORT", LOCAL_TESTING_PORT),
        }
    )
    socketio.run(
        app,
        debug=True,
        port=os.environ.get("PORT", LOCAL_TESTING_PORT),
        host=os.environ.get("ADDRESS", LOCAL_TESTING_IP),
        allow_unsafe_werkzeug=True
    )