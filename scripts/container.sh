#!/bin/bash

docker run \
	-it \
	-v "$PWD":/mnt \
	-w /mnt \
	--name="stock" \
	python:3 \
	/bin/bash
