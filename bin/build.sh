#!/bin/bash

cd /home/oa/VSCode/Goldoak-Service-Greenbone

docker build -t goldoak-module-greenbone:v0.7 .
docker tag goldoak-module-greenbone:v0.7 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.7
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.7


