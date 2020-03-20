# FROM alpine

FROM python:2.7

MAINTAINER Glauber Costa Vila Verde <glauber.vila.verde@gmail.com>

ENV APP_PATH=/app
ENV DIR_DATA=/data

RUN apt-get update && apt-get install -y \
		gcc \
		python-dev \
		libfreetype6-dev \
		libpng-dev \
		libffi-dev \
		gfortran \
		unzip \
		libgeos-3.7.1 \
		libgeos-dev \
		python3-numpy \
		vim \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
		setuptools \
		wheel \
		six==1.11.0 \
		certifi==2018.10.15 \
		pyOpenSSL==18.0.0 \
		cffi==1.11.5 \
		astropy==2.0.8 \
		spiceypy==2.1.2 \
		matplotlib==1.5.1 \
		Pillow==5.3.0 \
		OWSLib==0.17.0 \
		Cython==0.29 \
		pyproj==1.9.5.1 \
		pyshp==1.2.12 \
	&& pip freeze

RUN mkdir $APP_PATH

WORKDIR $APP_PATH

COPY . $APP_PATH

RUN cd ${APP_PATH}/basemap-1.1.0 \
		&& python setup.py install

# Download Finals for astropy
COPY iers_table.py $APP_PATH
RUN ./iers_table.py
