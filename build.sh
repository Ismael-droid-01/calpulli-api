#!/bin/bash
readonly CALPULLI_IMAGE_NAME=${1:-"calpulli:api-0.0.1a0"}
readonly PUSH_IMAGE=${2:-"0"}
readonly CACHE=${3:-"0"}

if [[ ${CACHE} -eq 0 ]]; then
    docker build --no-cache -t ${CALPULLI_IMAGE_NAME} -f Dockerfile .
else
    docker build -t ${CALPULLI_IMAGE_NAME} -f Dockerfile .
fi

if [[ ${PUSH_IMAGE} -eq 1 ]]; then
    docker push ${CALPULLI_IMAGE_NAME}
    exit 0
fi