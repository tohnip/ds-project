from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
   return render_template("index.html")

@app.route("/broadcast")
def broadcast():
    return render_template("live.html")

if __name__ == '__main__':
   app.run()
