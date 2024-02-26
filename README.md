# ds-project
Project repo for our group on distributed systems course

I'm using VSCode as my code editor. You can use what you wish, but at least that is a good one:
> https://code.visualstudio.com/

Download and install this for docker containers:
> https://www.docker.com/products/docker-desktop/

Possible troubleshooting with docker:

I had to add my user to a docker users group before I could run docker commands without sudo, but that might be just a WSL related issue. Anyway, this answered that issue:
> https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket


To try out your docker installation, try the following:
```
cd <your path>/ds-project
docker compose up --build
```
This will start three different nodes: broadcaster, server and consumer

The functionality is very simple at this point:

1. The broadcaster has some license free short story in the file source_material.json
2. The broadcaster reads that material, splits it into words and starts sending the words together with the story name to the server, one word every 2 seconds
3. Server uses Flask. It receives the words from broadcaster and stores them in working memory.
4. The consumer first requests a list of stories by name for it to "stream" and then requests that story one word every two seconds.

The command will leave every node logging to the console so it's a bit busy. You can look at the specific containers easily through docker desktop app.

You can also use your browser to access different paths on the server, try these when the containers are up and running:
> http://localhost:12345/
> http://localhost:12345/available_content
> http://localhost:12345/story/Bruce%20and%20the%20Spider%20by%20James%20Baldwin/1

On the last one try different numbers on the last place instead of just 1.

To stop the containers you need to just use CTRL+C on that terminal window.

To remove the containers you can use:
```
docker compose rm
```

You should see any running or stopped (but not removed) docker containers in your docker desktop program.


## Running without docker

The components can also be run without docker. You can use for example
```
python3 app.py
```
in the server folder to run the app just on your system. Notice that in that case the Flask server can be found from
> http://localhost:15000

Similarly other components can be run locally. When testing broadcaster, it's probably a good idea to start the server on a docker container and then run the broadcaster outside of a container. Just need to take care in choosing the correct ports and hosts when things are running outside docker!

> Easiest way to have only specific conteiners running would be to remove every container with the command above and then comment out the nodes you don't want running in the compose.yaml and starting with compose up again


## Web app
To run the web version that supports video streaming, spin up some CDNs by going to the `src/cdn` folder and running `python app.py <port number>` (don't use 5000 as this is reserved for the server). To start the main server, go to the `src/flaskapp` folder and run `python app.py`. Broadcasting and viewing can both be done in the browser at http://127.0.0.1:5000.
