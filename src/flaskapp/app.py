from flask import Flask, render_template, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
utilization = {i:0 for i in range(8)}
ip_map = {i:"http://127.0.0.1:500%d"%(i+1) for i in range(8)}
lives = {}
@app.route('/',methods=["GET"])
def index():
   return render_template("index.html")

@app.route("/broadcast",methods=["GET"])
def broadcast():
    return render_template("live.html")

@app.route("/get_cdn",methods=["GET"])
def get_cdn():
    min_util = 99999
    server_n = -1
    for i in range(8):
        if utilization[i] < min_util:
            min_util = utilization[i]
            server_n = i
            print(i,min_util)
    return {"server_n":server_n,"server_ip":ip_map[server_n]}

@app.route("/update_cdn/<server_n>/<startflag>",methods=["PUT"])
def update_util(server_n,startflag):
    stream_title = request.form.get("stream_title")
    lives[stream_title] = server_n
    utilization[int(server_n)] += int(startflag)*2-1
    print(utilization)
    return "OK"

@app.route("/end_stream",methods=["DELETE"])
def end_stream():
    stream_title = request.form.get("stream_title")
    utilization[lives[stream_title]] -= 1
    del lives[stream_title]

if __name__ == '__main__':
   app.run(host="127.0.0.1",port=5000)
