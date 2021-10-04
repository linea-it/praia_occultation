FROM python:2.7.17

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
	gfortran-7 \
	unzip \
	libgeos-3.7.1 \
	libgeos-dev \
	python3-numpy \
	vim \
	&& rm -rf /var/lib/apt/lists/*

# RUN pip install \
RUN pip install --upgrade pip \
	setuptools \
	wheel \
	six==1.11.0 \
	certifi==2018.10.15 \
	pyOpenSSL==18.0.0 \
	cffi==1.12 \
	numpy==1.12.0 \
	astropy==2.0.8 \
	spiceypy==2.1.2 \
	matplotlib==1.5.1 \
	Pillow==5.3.0 \
	OWSLib==0.17.0 \
	Cython==0.29 \
	pyproj==1.9.5.1 \
	pyshp==1.2.12 \
	SQLAlchemy==1.4.25 \
	psycopg2-binary==2.8.6 \
	pandas==0.24.2 \
	&& pip freeze

RUN mkdir $APP_PATH \
	&& chmod 775 $APP_PATH

WORKDIR $APP_PATH

# # Download Leap Second
# RUN wget --no-verbose --show-progress \
# 	--progress=bar:force:noscroll \ 
# 	-o naif0012.tls https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls

# Download da BSP planetary
# OBS. o Download demora bastante!
RUN wget --no-verbose --show-progress \
	--progress=bar:force:noscroll \ 
	-o de435.bsp https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de435.bsp


# Copia os arquivos do repositório para dentro da imagem
COPY . $APP_PATH

# # Unzip BSP Planetary
# RUN zip -F de435.bsp.zip --out single-archive.zip \
# 	&& unzip de435.bsp.zip \
# 	&& rm de435.bsp.zip single-archive.zip

# Compilar o geradata usando gfortran-7, Importante se não for esta versão da erro!
RUN cd ${APP_PATH}/src \
	&& gfortran-7 geradata.f -o geradata spicelib.a \
	# && mv geradata ${APP_PATH}/ \
	&& mv geradata /usr/local/bin/ \
	&& cd ${APP_PATH}

# Compilar o gerapositions usando gfortran-7, Importante se não for esta versão da erro!
RUN cd ${APP_PATH}/src \
	&& gfortran-7 gerapositions.f -o gerapositions \
	&& mv gerapositions /usr/local/bin/ \
	&& cd ${APP_PATH}

# Compilar o elimina.f usando gfortran-7, Importante se não for esta versão da erro!
RUN cd ${APP_PATH}/src \
	&& gfortran-7 elimina.f -o elimina \
	&& mv elimina /usr/local/bin/ \
	&& cd ${APP_PATH}


# RUN cd ${APP_PATH}/basemap-1.1.0 \
# 	&& python setup.py install

# # Download Finals for astropy
# COPY iers_table.py $APP_PATH
# RUN ./iers_table.py


# Criar o grupo des-brazil com o mesmo id usado no linea
RUN groupadd --gid 10000 des-brazil

# Adicionar o usuario appuser para rodar os jobs no condor
RUN useradd --no-create-home --gid des-brazil --uid 1000 appuser

# Adiciona o usuario Glauber porque quando o HTCondor roda está imagem é com o usuario que submeteu.
RUN useradd --no-create-home --gid des-brazil --uid 10139 glauber.costa



# Troca o usuario para um que não é ROOT!
USER appuser

