FROM continuumio/miniconda3

LABEL org.opencontainers.image.authors="l.archer@leeds.ac.uk, gyrc@leeds.ac.uk, h.p.rice@leeds.ac.uk, n.m.lomax@leeds.ac.uk"

# Install some packages 
RUN apt-get update && apt-get install -y \
	sudo \
	git \
	build-essential \
	p7zip-full \
	bash \
	nano \
	vim \
	libssl-dev \
	libcurl4-openssl-dev \
	libxml2-dev \
    libudunits2-dev
# 	r-base \

# set home directory for project
WORKDIR /home/docker/

# clone Minos repo
RUN git clone -b main --single-branch https://github.com/Leeds-MRG/Minos.git

# Start in Minos/
WORKDIR /home/docker/Minos/

## Set up conda env
# See https://stackoverflow.com/questions/59289917/how-to-use-a-yaml-file-with-dockerfile-to-activate-conda-environment for more details
ADD environment.yml /tmp/environment.yml
RUN conda env create --file /tmp/environment.yml
# Run conda activate and modify bashrc to open container with env enabled
RUN echo "conda activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" >> ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

ENV CONDA_DEFAULT_ENV $(head -1 /tmp/environment.yml | cut -d' ' -f2)

RUN ["/bin/bash", "-c", "echo Hello World!"]
