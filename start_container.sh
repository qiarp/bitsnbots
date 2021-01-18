#!/bin/bash

# copia db-todo.json atual do container para o host
containerid=$(sudo docker ps | grep "bnbytes/bots" | awk '{print $1}')
sudo docker cp "$containerid":./db-todo.json db-todo.json

# builda
sudo docker build -t bnbytes/bots .

# start
sudo docker run -it bnbytes/bots
