from flask import Flask, request
import logging
import sys

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

app = Flask("Server node flask")

content_storage = {} 


@app.route("/")
def show_help():
    return "<p> You can send textual data to this server to the path /send_data</p>"

@app.post("/send_data")
def receive_sent_data():
    logging.info({"message": "Got a request", "request.json": request.json})
    json_data = request.json
    if "name" not in json_data or "content_part" not in json_data:
        return {"message": "receive failed, incorrect keys in json data", "correct keys": "name,content_part"}, 400

    if json_data["name"] not in content_storage:
        content_storage[json_data["name"]] = [json_data["content_part"]]
    else:
        content_storage[json_data["name"]].append(json_data["content_part"])

    return {"message": "your data was received, thank you"}, 200

@app.route("/all_data")
def get_all_data():
    return content_storage

@app.route("/story/<story_name>/<int:part_id>")
def get_next_part(story_name, part_id):
    if story_name not in content_storage:
        return {"message": "story name wasn't found in library", "story name": story_name}, 400
    elif len(content_storage[story_name]) < part_id:
        return {"message": "Story isn't that long (yet)", "story name": story_name, "story_length": len(content_storage[story_name])}, 400
    else:
        return {"new part": content_storage[story_name][part_id-1], "next_id": part_id+1}, 200

@app.route("/available_content")
def get_titles():
    return {"Available stories": [key for key in content_storage.keys()]}, 200


if __name__ == "__main__":
    app.run(debug=True, port=15000, host="0.0.0.0")