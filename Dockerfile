FROM python:3
MAINTAINER HsuBokai

RUN pip install --upgrade pip && \
	pip install --no-cache-dir --upgrade lxml && \
	pip install --no-cache-dir requests && \
	pip install --no-cache-dir numpy && \
	pip install --no-cache-dir pandas && \
	pip install --no-cache-dir matplotlib
