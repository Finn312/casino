#!/bin/bash 
docker stop casino
docker rm casino
git pull
docker build -t casino .
docker run -d -p 8000:8000 -v casino_data:/app/database --name casino casino

