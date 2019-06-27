# stole, without shame, from:
# https://gist.github.com/nvgoldin/9dc71efc95fb7319f15fa56a5d60deb8
FROM python:3.7-alpine3.8
RUN apk add --no-cache \
            --allow-untrusted \
            --repository \
            http://dl-3.alpinelinux.org/alpine/edge/testing \
            hdf5 hdf5-dev && \
    apk add --no-cache \
            build-base
RUN pip install --no-cache-dir --no-binary :all: h5py
RUN apk --no-cache del build-base

RUN apk --update add \
      build-base libffi-dev openssl-dev python3-dev \
      libffi openssl ca-certificates python3
RUN pip3 install --no-cache-dir requests zope.interface https://files.pythonhosted.org/packages/source/T/Twisted/Twisted-17.1.0.tar.bz2
RUN apk --no-cache del build-base openssl-dev python3-dev

ADD coinbase.py /coinbase.py

ENTRYPOINT python3 /coinbase.py