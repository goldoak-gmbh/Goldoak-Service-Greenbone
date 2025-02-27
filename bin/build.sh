#!/bin/bash

docker build -t goldoak-module-greenbone:v0.4 .
docker tag goldoak-module-greenbone:v0.4 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.4
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.4
