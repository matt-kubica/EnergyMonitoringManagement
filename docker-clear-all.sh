#!/bin/bash

docker kill $(docker ps -q) # stop all containers
docker rm $(docker ps -a -q) # remove all containers 
docker rmi $(docker images -q) # remove all images
docker network prune # remove all networks
docker volume prune # remove all volumes