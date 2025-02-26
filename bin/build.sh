#!/bin/bash

docker build -t goldoak-module-greenbone:v0.3 .
docker tag goldoak-module-greenbone:v0.3 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.3
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.3
