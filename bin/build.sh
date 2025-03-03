#!/bin/bash

cd /home/oa/VSCode/Goldoak-Service-Greenbone

docker build -t goldoak-module-greenbone:v0.6 .
docker tag goldoak-module-greenbone:v0.6 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.6
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.6


