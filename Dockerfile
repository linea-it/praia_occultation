FROM python:2.7.17

MAINTAINER Glauber Costa Vila Verde <glauber.vila.verde@gmail.com>

ENV APP_PATH=/app
ENV DIR_DATA=/tmp/data

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
	csh \
	gnuplot \
	ghostscript \
	libxft-dev \
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
	numpy==1.16.6 \
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
	&& chmod 777 $APP_PATH

WORKDIR $APP_PATH

# Download da BSP planetary
# OBS. o Download demora bastante!
RUN wget --no-verbose --show-progress \
	--progress=bar:force:noscroll \ 
	https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de435.bsp

# Download Leap Second
RUN wget --no-verbose --show-progress \
	--progress=bar:force:noscroll \
	https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls

# Instalação do PRAIA OCC
COPY ./praia_occ_src $APP_PATH/praia_occ_src
# Importante! Compilar o PRAIA OCC usando gfortran-7, 
# se não for esta versão da erro!
RUN cd ${APP_PATH}/praia_occ_src \
	&& gfortran-7 geradata.f -o geradata spicelib.a \
	&& mv geradata /usr/local/bin/ \
	&& gfortran-7 elimina.f -o elimina \
	&& mv elimina /usr/local/bin/ \
	&& gfortran-7 PRAIA_occ_star_search_12.f -o PRAIA_occ_star_search_12 \
	&& mv PRAIA_occ_star_search_12 /usr/local/bin/ \
	# 	&& gfortran-7 gerapositions.f -o gerapositions \
	# 	&& mv gerapositions /usr/local/bin/ \
	&& cd ${APP_PATH} \
	&& rm -r ${APP_PATH}/praia_occ_src

# RUN cd ${APP_PATH}/basemap-1.1.0 \
# 	&& python setup.py install

# # Download Finals for astropy
# COPY iers_table.py $APP_PATH
# RUN ./iers_table.py

# Instalação do NIMAv7
COPY ./nima_src $APP_PATH/nima_src
RUN set -ex \
	&& cd $APP_PATH/nima_src \
	&& tar -xvf NIMAv7.tar.gz \
	&& cd NIMAv7 \
	&& tar -xvf NIMAv7_public.tar.gz \
	&& tar -xvf NIMAv7_user.tar.gz \
	&& rm NIMAv7_public.tar.gz NIMAv7_user.tar.gz \
	&& mv $APP_PATH/nima_src/NIMAv7 $APP_PATH/NIMAv7 \
	# Instalação do Nima Public
	&& cd $APP_PATH/NIMAv7/NIMAv7_public/data \
	&& ./sc_listobs.sh \
	&& ln -s de432/de432.lnx de.lnx \
	&& ln -s bias.cat bias.dat \
	# Extrai as dependencias
	&& mkdir $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& cd $APP_PATH/nima_src \
	&& tar -xvf sofa_f-20160503_c.tar.gz -C $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& tar -xvf toolkit.tar.Z -C $APP_PATH/NIMAv7/NIMAv7_public/lib \
	# Instalação do SOFA
	&& cd $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& cd sofa/20160503_c/f77/src \
	&& make \
	&& cd $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& ln -s sofa/20160503_c/f77/src/libsofa.a sofa.a \
	# Instalação do SPICE
	&& cd $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& cd toolkit \
	&& ./makeall.csh \
	&& cd $APP_PATH/NIMAv7/NIMAv7_public/lib \
	&& ln -s toolkit/lib/spicelib.a spice.a \
	# Install NIMA User
	&& cd $APP_PATH/NIMAv7/NIMAv7_user \
	&& mkdir obs data ci jplbsp lib exe results \
	&& ln -s $APP_PATH/NIMAv7/NIMAv7_public/data/listobsUAI.dat data/listobsUAI.dat \
	&& ln -s $APP_PATH/NIMAv7/NIMAv7_public/data/de.lnx data/de.lnx \
	&& ln -s $APP_PATH/NIMAv7/NIMAv7_public/data/bias.dat data/bias.dat \
	&& ln -s $APP_PATH/NIMAv7/NIMAv7_public/lib/sofa.a lib/sofa.a \
	&& ln -s $APP_PATH/NIMAv7/NIMAv7_public/lib/spice.a lib/spice.a \
	&& echo "${APP_PATH}/NIMAv7/NIMAv7_public"|./compil.sh \
	# Remove o diretório com os fontes.
	&& rm -r $APP_PATH/nima_src \
	# Adiciona Permissão de Grupo na pasta NIMAv7
	&& chmod -R g+w $APP_PATH/NIMAv7 \
	&& cd $APP_PATH


# Copia os programas python para a pasta app
COPY ./src $APP_PATH

# Criar o grupo des-brazil com o mesmo id usado no linea
RUN groupadd --gid 10000 des-brazil

# Adicionar o usuario appuser para rodar os jobs no condor
RUN useradd --no-create-home --gid des-brazil --uid 1000 appuser

# Adiciona o usuario Glauber porque quando o HTCondor roda está imagem é com o usuario que submeteu.
RUN useradd --no-create-home --gid des-brazil --uid 10139 glauber.costa

# Troca o usuario para um que não é ROOT!
USER appuser
