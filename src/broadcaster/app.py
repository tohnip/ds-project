from flask import Flask, render_template
app = Flask(__name__)
utilization = {i:0 for i in range(7)}
@app.route('/',methods=["GET"])
def index():
   return render_template("index.html")

@app.route("/broadcast",methods=["GET"])
def broadcast():
    return render_template("live.html")

@app.route("get_cdn",methods=["GET"])
def get_cdn():



if __name__ == '__main__':
   app.run()
