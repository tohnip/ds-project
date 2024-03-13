from flask import Flask, request, send_file
from flask_cors import CORS
from sys import argv
import datetime
import io
import requests
import os
import time
import sys
import logging
from flask_socketio import SocketIO, emit, rooms, leave_room, join_room, close_room


LOCAL_TESTING_IP = "127.0.0.1"
LOCAL_TESTING_HOSTNAME = "the_only_server"
LOCAL_TESTING_PORT = 10001


handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins=['http://127.0.0.1:5000', 'http://localhost:5000', '*'])
latest_chunks = {}


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
    
    # response = requests.post(f"http://{os.environ['LOAD_BALANCER_HOSTNAME']}:{os.environ['LOAD_BALANCER_PORT']}/register_new_stream",
    #                          json={
    #                              "streamid": data["streamid"],
    #                              "hostname": os.environ.get("HOSTNAME", LOCAL_TESTING_HOSTNAME),
    #                          }
    #                          )

    # if response.status_code != 200:
    #     logging.warning({"message": "registering a stream to load balancer failed", "stream name": data["streamid"]})
    #     emit("stream_registration_response", {"result": "failure", "reason": "couldn't register the stream"})
    #     return


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


@app.route("/upload_chunk",methods=["POST"])
def upload_chunk():
    streamid = request.form.get('streamid')
    if request.form.get("msg"):
        latest_chunks[streamid] = request.form.get("msg")
    else:
        tmp = request.files.get("chunk").read()
        f = io.BytesIO(tmp)
        latest_chunks[streamid] = f

    return "OK"

#if a request comes in before a stream is established, latest_chunks will have a dummy value for the streamid and return that as a signal to await
#if a request comes in and the stream has stopped, notify

@app.route("/download_chunk/<streamid>",methods=["GET"])
def download_chunk(streamid):
    if type(latest_chunks[streamid])==str:
        logging.info({"message": "sending message"})
        return {"msg":latest_chunks[streamid]}
    logging.info({"message": "sending file", "file size": latest_chunks[streamid].getbuffer().nbytes})
    return send_file(latest_chunks[streamid],mimetype="video/webm")

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
    time.sleep(2)
    requests.post(
        url=f"http://{os.environ['LOAD_BALANCER_HOSTNAME']}:{os.environ['LOAD_BALANCER_PORT']}/register_server",
        json={
            "address": "127.0.0.1", #os.environ.get("ADDRESS", LOCAL_TESTING_IP),
            "hostname": os.environ.get("HOSTNAME", LOCAL_TESTING_HOSTNAME),
            "port": os.environ.get("OUTSIDE_PORT", LOCAL_TESTING_PORT),
        }
    )
    socketio.run(
        app,
        debug=True,
        port=os.environ.get("PORT", LOCAL_TESTING_PORT),
        host=os.environ.get("ADDRESS", LOCAL_TESTING_IP),
        allow_unsafe_werkzeug=True
    )
