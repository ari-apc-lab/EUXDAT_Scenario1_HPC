#!/bin/bash

rm -rf src
cp -R ../src src

export IMAGE_NAME=euxdat-olu-frontend
docker build --rm=true --no-cache -t $IMAGE_NAME . 
docker tag $IMAGE_NAME registry.test.euxdat.eu/euxdat/$IMAGE_NAME
docker push registry.test.euxdat.eu/euxdat/$IMAGE_NAME

rm -rf src
