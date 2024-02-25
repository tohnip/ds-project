import logging
import sys
import time
import json

from flask import Flask, request, redirect, url_for, Response

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

IP = "127.0.0.1"
IP = "0.0.0.0"  # Comment this out if you run this server outside docker

app = Flask("Server node flask")
content_storage = {} 

streamers = {}
streams = {}


# Holds information about servers, their addresses, socketio ports and reported load levels
server_status = {}

""" Sever related routes """

@app.post("/register_server")
def register_new_server():
    data = request.get_json()
    logging.info({"message": "new server registered", "server info": data})
    hostname = data["hostname"]
    if hostname not in server_status:
        server_status[hostname] = {"address": data["address"], "port": data["port"], "load": 0}

    return "Successs"

@app.post("/register_new_stream")
def store_new_stream():
    stream_data = request.get_json()
    logging.info({"message": "new stream registered", "data": stream_data})
    streams[stream_data["stream_name"]] = {"hostname": stream_data["hostname"], "port": server_status[stream_data["hostname"]]["port"]}

    return Response("", status=200)

""" Broadcaster related routes """

@app.route("/request_server")
def assign_server():
    """ There is still an issue: what if multiple broadcasters ask for a server at the same time?
     There should be some estimate on how much load one broadcaster causes and limit with that.
      Or maybe lock the server assignment until we have load information?
       Lock some variable to make atomic increments into some load estimate to prevent too many streams from being assigned to one server?  """
    for hostname, host_data in server_status.items():
        if host_data["load"] <  10:
            logging.info({"message": "assigned a server to a broadcaster", "hostname": hostname})
            return {"hostname": hostname, "port": host_data["port"], "address": host_data["address"]}
    
    logging.warning({"message": "didn't assign any servers for a broadcaster"})




""" Consumer related routes """

@app.route("/")
def show_help():
    return redirect(url_for("show_streams"))


@app.get("/streams")
def show_streams():
    if not streams:
        logging.warning({"message": "consumer requested streams but we don't have any"})
        return Response("We don't have any streams at this moment", status=503)

    if "stream_name" in request.args:
        stream_name = request.args.get("stream_name")
        if stream_name not in streams:
            logging.warning({"message": "consumer requested a stream that we don't have", "stream name": stream_name})
            return Response("We don't have that stream at the moment", status=503)
        else:
            return streams[stream_name]
    else:
        return {"streams": [key for key in streams.keys()]}


if __name__ == "__main__":
    app.run(debug=True, port=15000, host=IP)