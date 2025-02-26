#!/bin/bash

docker build -t goldoak-module-greenbone:v0.2 .
docker tag goldoak-module-greenbone:v0.2 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.2
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.2
