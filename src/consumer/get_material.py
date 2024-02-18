import requests
import logging
import time
import sys
import json
import socketio

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
            #logging.info({"event_name": response[0], "data": response[1]})




    return

    got_healthy_response = True
    while got_healthy_response:
        got_healthy_response = False

        response = requests.get("http://server:15000/available_content")
        if response.status_code != 200:
            logging.warning({"message": "get request failed", "response": response})

        json_content = json.loads(response.content)
        logging.info({"message": "received content", "content": json_content})

        for story_name in json_content["Available stories"]:
            part_ind = 1
            while True:
                response = requests.get(f"http://server:15000/story/{story_name}/{part_ind}")
                if response.status_code != 200:
                    logging.warning({"message": "get request failed", "response content": response.content})
                    break
                
                got_healthy_response = True

                json_response = json.loads(response.content)

                logging.info(json_response["new part"])
                part_ind = int(json_response["next_id"])

                time.sleep(2)


if __name__ == '__main__':
    time.sleep(3)
    main()
