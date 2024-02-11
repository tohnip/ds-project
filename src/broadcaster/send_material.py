import requests
import logging
import json
import time
import sys

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)


def main():
    logging.info({"message": "started running broadcaster"})
    source_data = ""
    with open("source_material.json", "r") as source_json:
        source_data = json.load(source_json)

    if source_data == "":
        raise Exception("Source material loading failed")

    logging.info({"message": "loaded source material", "material": source_data})

    while True:
        for word in source_data["content"].split(" "):
            response = requests.post(
                'http://server:15000/send_data',
                json={"name": source_data["file name"], "content_part": word, },
            )
            if response.status_code != 200:
                logging.warning({"message": "post request failed", "response": response})
            else:
                logging.info({"message": "successfully sent the message", "content": word})
            
            time.sleep(2)

if __name__ == '__main__':
    time.sleep(2)
    main()
