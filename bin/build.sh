#!/bin/bash

docker build -t goldoak-module-greenbone:v0.1 .
docker tag goldoak-module-greenbone:v0.1 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.1
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.1