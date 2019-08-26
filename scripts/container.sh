#!/bin/bash

docker run \
	-it \
	--rm \
	-v "$PWD":/mnt \
	python:3 \
	/bin/bash
