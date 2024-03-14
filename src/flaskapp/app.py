
import datetime
import hashlib
import logging
import os
import sys

from flask import Flask, render_template, request, Response
from flask_cors import CORS


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


def get_lowest_util():
    min_util = 99999999
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

    hostname = data["hostname"]
    if hostname not in server_status:
        server_status[hostname] = {"address": data["address"], "port": data["port"], "load": 0}
        logging.info({
            "message": "new server registered",
            "server info": data,
            "server utilizations": {hostname: cdn["load"] for hostname, cdn in server_status.items()},
        })

        return "Successs"
    else:
        logging.warning({
            "message": "new server requested registration, but hostname was already in use",
            "server info": data,
            "server utilizations": {hostname: cdn["load"] for hostname, cdn in server_status.items()},
        })

        return Response("We already have a CDN with your hostname", status=400)


@app.route('/',methods=["GET"])
def index():
   return render_template("index.html")


@app.route("/broadcast",methods=["GET"])
def broadcast():
    return render_template("live.html")


@app.route("/get_cdn/<streamid>",methods=["GET"])
def get_cdn(streamid):
    return_data = {
        'server_address': server_status[lives_map[streamid]]["address"],
        'server_port': server_status[lives_map[streamid]]["port"],
    }
    
    logging.info({
        "message": "CDN address requested",
        "streamid": streamid,
        "cdn data": return_data,
        "server utilizations": {hostname: cdn["load"] for hostname, cdn in server_status.items()},
    })
    return return_data


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

    logging.info({
        "message": "created a stream",
        "streamid": streamid,
        "title": title,
        "server utilizations": {hostname: cdn["load"] for hostname, cdn in server_status.items()},
    })

    return {"streamid":streamid}


@app.route("/delete_stream", methods=["POST"])
def delete_stream():
    streamid = request.form.get("streamid")
    title = titles_map[streamid]

    server_status[lives_map[streamid]]["load"] -= 1
    del lives_map[streamid]
    del titles_map[streamid]

    logging.info({
        "message": "deleted a stream",
        "streamid": streamid,
        "title": title,
        "server utilizations": {hostname: cdn["load"] for hostname, cdn in server_status.items()},
    })

    return "OK"


if __name__ == '__main__':
    app.run(
       host=os.environ["ADDRESS"],
       port=os.environ["PORT"],
    )
