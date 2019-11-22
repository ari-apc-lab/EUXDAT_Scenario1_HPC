#!/bin/bash

export IMAGE_NAME=alpine:test
docker build --rm=true --no-cache -t $IMAGE_NAME . 
docker tag $IMAGE_NAME registry.test.euxdat.eu/euxdat/$IMAGE_NAME
docker push registry.test.euxdat.eu/euxdat/$IMAGE_NAME
