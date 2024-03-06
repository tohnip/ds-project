from flask import Flask, render_template, request
from flask_cors import CORS
import hashlib
import datetime
import base64
app = Flask(__name__)
CORS(app)
utilization = {"http://127.0.0.1:500%d"%(i+1):0 for i in range(2)}
lives_map = {}
titles_map = {}
#helper function
def get_lowest_util():
    min_util = 99999999
    server_id = ""
    for u in utilization:
        if utilization[u] < min_util:
            min_util = utilization[u]
            server_id = u
    return server_id

@app.route('/',methods=["GET"])
def index():
   return render_template("index.html")

@app.route("/broadcast",methods=["GET"])
def broadcast():
    return render_template("live.html")

@app.route("/get_cdn/<streamid>",methods=["GET"])
def get_cdn(streamid):
    return {'server_id':lives_map[streamid]}
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
    server_id = get_lowest_util()
    utilization[server_id] += 1
    lives_map[streamid] = server_id
    titles_map[streamid] = title
    return {"streamid":streamid}

@app.route("/update_stream",methods=["POST"])
def update_stream():
    streamid = request.form.get("streamid")
    new_server_id = get_lowest_util()
    utilization[lives_map[streamid]] -= 1
    utilization[new_server_id] += 1
    lives_map[streamid] = new_server_id
    return "OK"

@app.route("/delete_stream",methods=["POST"])
def delete_stream():
    streamid = request.form.get("streamid")
    utilization[lives_map[streamid]] -= 1
    del lives_map[streamid]
    return "OK"

if __name__ == '__main__':
   app.run(host="127.0.0.1",port=5000)
