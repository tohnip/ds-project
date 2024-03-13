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
latest_chunks = {}

@app.route("/",methods=["GET"])
def index():
    return "You probably shouldn't be here."

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
    app.run(
       host=os.environ.get("ADDRESS", LOCAL_TESTING_IP),
       port=os.environ.get("PORT", LOCAL_TESTING_PORT)
    )
