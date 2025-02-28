#!/bin/bash

docker build -t goldoak-module-greenbone:v0.5 .
docker tag goldoak-module-greenbone:v0.5 ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.5
docker push ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.5
