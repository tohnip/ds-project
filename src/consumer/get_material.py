import json
import logging
import requests
import socketio
import sys
import time

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)

hostname = "localhost"
hostname = "server"  # comment this out if you want to run without docker


def main():
    logging.info({"message": "started running consumer"})

    response = requests.get(f"http://{hostname}:15000/streams")
    stream_names = json.loads(response.content)["streams"]
    logging.info({"message": "received available streams", "streams": stream_names})
    stream_name = stream_names[0]
    if not stream_name:
        return

    with socketio.SimpleClient() as sio:
        sio.connect(f"http://{hostname}:15000", transports=['websocket'])

        logging.info({"message": "requesting new steam", "stream name": stream_name})
        sio.emit("watch_stream", {"stream_name": stream_name})
        while True:
            response = sio.receive()
            logging.info(response[1])


if __name__ == '__main__':
    # delay the start so that server and broadcaster have time to start before this
    time.sleep(3)
    main()
