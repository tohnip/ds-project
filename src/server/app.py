from flask import Flask, request
from flask_socketio import SocketIO, emit, rooms, leave_room, join_room, close_room
import logging
import sys
import json
import time

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

@socketio.on('broadcast_connect')
def handle_new_broadcaster():
    logging.info({"message": "received new broadcast connection through socketio"})

# @socketio.on('connect')
# def handle_new_connection():
#     logging.info({"message": "received new connection through socketio", "param1": "param1"})
#     emit("random response", {"server asd": "asdasd server"})
#     logging.info("emitted response")

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

    
@socketio.on('message')
def message(data):
    logging.info(data)
    #emit("Another random response")


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



@app.get("/streams")
def show_streams():
    return {"streams": [key for key in streams.keys()]}


@app.route("/")
def show_help():
    return "<p> You can send textual data to this server to the path /send_data</p>"

@app.post("/send_data")
def receive_sent_data():
    logging.info({"message": "Got a request", "request.json": request.json})
    json_data = request.json
    if "name" not in json_data or "content_part" not in json_data:
        return {"message": "receive failed, incorrect keys in json data", "correct keys": "name,content_part"}, 400

    if json_data["name"] not in content_storage:
        content_storage[json_data["name"]] = [json_data["content_part"]]
    else:
        content_storage[json_data["name"]].append(json_data["content_part"])

    return {"message": "your data was received, thank you"}, 200

@app.route("/all_data")
def get_all_data():
    return content_storage

@app.route("/story/<story_name>/<int:part_id>")
def get_next_part(story_name, part_id):
    if story_name not in content_storage:
        return {"message": "story name wasn't found in library", "story name": story_name}, 400
    elif len(content_storage[story_name]) < part_id:
        return {"message": "Story isn't that long (yet)", "story name": story_name, "story_length": len(content_storage[story_name])}, 400
    else:
        return {"new part": content_storage[story_name][part_id-1], "next_id": part_id+1}, 200

@app.route("/available_content")
def get_titles():
    return {"Available stories": [key for key in content_storage.keys()]}, 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=15000, host=IP, allow_unsafe_werkzeug=True)