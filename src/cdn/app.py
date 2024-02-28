from flask import Flask, request, send_file
from flask_cors import CORS
from sys import argv
import datetime
import io
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
        f = io.BytesIO(request.files.get("chunk").read())
        latest_chunks[streamid] = f

    return "OK"

#if a request comes in before a stream is established, latest_chunks will have a dummy value for the streamid and return that as a signal to await
#if a request comes in and the stream has stopped, notify

@app.route("/download_chunk/<streamid>",methods=["GET"])
def download_chunk(streamid):
    print(latest_chunks, datetime.datetime.now(), "\n", "\n", "\n")



    if type(latest_chunks[streamid])==str:
        return {"msg":latest_chunks[streamid]}
    return send_file(latest_chunks[streamid],mimetype="video/webm")


if __name__ == '__main__':
   app.run(host="127.0.0.1",port=int(argv[1]))
