import requests
import logging
import json
import time
import sys

import socketio

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)


hostname = "localhost"
hostname = "load_balancer"  # comment this out if you want to run without docker


def main():
    logging.info({"message": "started running broadcaster"})

    source_data = ""
    with open("source_material.json", "r") as source_json:
        source_data = json.load(source_json)

    if source_data == "":
        raise Exception("Source material loading failed")

    logging.info({"message": "loaded source material", "material": source_data})

    while True:

        response = requests.get(f"http://{hostname}:15000/request_server")
        if response.status_code != 200:
            logging.warning({"message": "requesting a server failed", "response": response})
            time.sleep(2)
            continue
        else:
            logging.info({"message": "successfully got a server", "content": response})
        
        json_data = response.json()
        logging.info({"message": "assigned server data", "data": json_data})
        server_hostname = json_data["hostname"]
        server_port = json_data["port"]

        with socketio.SimpleClient() as sio:
            sio.connect(f"http://{server_hostname}:{server_port}", transports=['websocket'])

            sio.emit("register_new_stream", {"stream_name": source_data["file name"]})
            response = sio.receive()
            if response[1]["result"] != "success":
                time.sleep(4)
                continue

            while True:
                sio.emit("message", f"\nYou will now hear the story of {source_data['file name']}:\n")
                connection_healthy = True

                for word in source_data["content"].split(" "):
                    sio.emit("broadcast_data", word)

                    response = sio.receive()
                    logging.info(response)
                    if response[1]["result"] != "success":
                        connection_healthy = False
                        break

                    time.sleep(0.4)

                if not connection_healthy:
                    break

    # while True:
    #     for word in source_data["content"].split(" "):
    #         response = requests.post(
    #             'http://server:15000/send_data',
    #             json={"name": source_data["file name"], "content_part": word, },
    #         )
    #         if response.status_code != 200:
    #             logging.warning({"message": "post request failed", "response": response})
    #         else:
    #             logging.info({"message": "successfully sent the message", "content": word})
            
    #         time.sleep(2)

if __name__ == '__main__':
    time.sleep(4)
    main()
