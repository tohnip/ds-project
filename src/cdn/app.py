from flask import Flask, request
from flask_cors import CORS
from sys import argv
from time import sleep
app = Flask(__name__)
CORS(app)

@app.route("/",methods=["GET"])
def index():
    return "You probably shouldn't be here."

@app.route("/upload_chunk",methods=["POST"])
def upload_chunk():
    print(request.files.get('chunk'))
    for f in request.files.items():
        print(f)
    sleep(1)
    return "OK"

if __name__ == '__main__':
   app.run(host="127.0.0.1",port=int(argv[1]))
