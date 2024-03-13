from flask import Flask, render_template, request, Response
from flask_cors import CORS
import hashlib
import datetime
import base64
import requests
import os
import time
import logging
import sys

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
server_status = {}
lives_map = {}
titles_map = {}
#helper function
def get_lowest_util():
    min_util = 99999999
    logging.info(server_status)
    server_address = list(server_status.keys())[0]
    for hostname, cdn in server_status.items():
        load = cdn["load"]
        if load < min_util:
            min_util = load
            server_address = hostname
    return server_address


@app.post("/register_server")
def register_new_server():
    data = request.get_json()
    logging.info({"message": "new server registered", "server info": data})
    hostname = data["hostname"]
    if hostname not in server_status:
        server_status[hostname] = {"address": data["address"], "port": data["port"], "load": 0}
        return "Successs"
    else:
        return Response("We already have a CDN with your hostname", status=400)


@app.route('/',methods=["GET"])
def index():
   return render_template("index.html")

@app.route("/broadcast",methods=["GET"])
def broadcast():
    return render_template("live.html")

@app.route("/get_cdn/<streamid>",methods=["GET"])
def get_cdn(streamid):
    logging.info(server_status)
    logging.info(lives_map)
    return_data = {
        'server_address': server_status[lives_map[streamid]]["address"],
        'server_port': server_status[lives_map[streamid]]["port"],
    }
    logging.info(return_data)
    return return_data
#when we create_stream a stream, assign a streamid and cdn to it immediately (based on least utilized)
#when update_stream is called, we update the cdn to the least utilized one
#when end_stream is called, we decrement utilization for its cdn and remove the streamid from the list


@app.route("/view",methods=["GET"])
def lives():
    return render_template("view.html",streams=titles_map)

@app.route("/view/<streamid>",methods=["GET"])
def view(streamid):
    return render_template("watch.html",title=titles_map[streamid],streamid=streamid)

@app.route("/create_stream",methods=["POST"])
def create_stream():
    title = request.form.get("title")
    streamid = hashlib.md5((title+str(datetime.datetime.now())).encode("utf-8")).hexdigest()
    sever_hostname = get_lowest_util()
    server_status[sever_hostname]["load"] += 1
    lives_map[streamid] = sever_hostname
    titles_map[streamid] = title
    return {"streamid":streamid}

@app.route("/update_stream",methods=["POST"])
def update_stream():
    streamid = request.form.get("streamid")
    new_server_id = get_lowest_util()
    if server_status[lives_map[streamid]]["load"] - server_status[new_server_id]["load"] > 1:
        server_status[lives_map[streamid]]["load"] -= 1
        server_status[new_server_id]["load"] += 1
        lives_map[streamid] = new_server_id
    return "OK"

@app.route("/delete_stream",methods=["POST"])
def delete_stream():
    streamid = request.form.get("streamid")
    server_status[lives_map[streamid]]["load"] -= 1
    del lives_map[streamid]
    return "OK"


if __name__ == '__main__':
    app.run(
       host=os.environ.get("ADDRESS", LOCAL_TESTING_IP),
       port=os.environ.get("PORT", LOCAL_TESTING_PORT)
    )
