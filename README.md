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
docker build -t ds-project .
docker run --name simple-http-server -dp 127.0.0.1:3000:3000 ds-project
```
Go to
> http://localhost:3000/

You should see a Directory listing of this repo at this time. This will obviously change.

To stop the docker image for what ever reason, like restarting after changes, use
```
docker rm simple-http-server
```

You should see any running or stopped (but not removed) docker containers in your docker desktop program.