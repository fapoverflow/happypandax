#!/bin/sh
cd ..
#USER_NAME="TODO"
#USER_ID=TODO
#GROUP_NAME="TODO"
#GROUP_ID=TODO
#ZONE="TODO"
#TAG="your_dockerhub_username/happypandax:0.13.3" # TODO
docker build . --tag $TAG \
  --build-arg USER_NAME=$USER_NAME --build-arg USER_ID=$USER_ID \
  --build-arg GROUP_NAME=$GROUP_NAME --build-arg GROUP_ID=$GROUP_ID \
  --build-arg ZONE=$ZONE