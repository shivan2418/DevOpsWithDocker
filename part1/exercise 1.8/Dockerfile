FROM ubuntu:20.04
RUN apt update && apt-get install curl -y
CMD echo "Input website:"; read website; echo "Searching.."; sleep 1; curl http://$website;

