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
hostname = "load_balancer"  # comment this out if you want to run without docker


def main():
    logging.info({"message": "started running consumer"})

    while True:
        response = requests.get(f"http://{hostname}:15000/streams")
        stream_names = json.loads(response.content)["streams"]
        logging.info({"message": "received available streams", "streams": stream_names})
        stream_name = stream_names[0]
        if not stream_name:
            time.sleep(2)
            continue
        
        response = requests.get(f"http://{hostname}:15000/streams", params={"stream_name": stream_name})
        json_data = json.loads(response.content)
        stream_host = json_data["hostname"]
        stream_port = json_data["port"]

        with socketio.SimpleClient() as sio:
            sio.connect(f"http://{stream_host}:{stream_port}", transports=['websocket'])

            logging.info({"message": "requesting new steam", "stream name": stream_name})
            sio.emit("watch_stream", {"stream_name": stream_name})
            while True:
                response = sio.receive()
                logging.info(response[1])


if __name__ == '__main__':
    # delay the start so that server and broadcaster have time to start before this
    time.sleep(6)
    main()
