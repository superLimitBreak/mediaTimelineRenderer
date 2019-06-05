FROM python:alpine3.8 as base

# ffmpeg:alpine is built against alpine 3.8 - so we need the python base image in sync
COPY --from=jrottenberg/ffmpeg:4.1-alpine /usr/local /usr/local
RUN apk add --no-cache --update libgcc libstdc++ ca-certificates libcrypto1.0 libssl1.0 libgomp expat git
ENV PATH="/usr/local/bin:${PATH}"
RUN ffmpeg -h

COPY mediaTimelineRenderer.pip requirements.pip

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache \
        --virtual .build-deps build-base linux-headers git &&\
    pip3 install --no-cache-dir -r requirements.pip &&\
    apk del .build-deps

WORKDIR /mediaTimelineRenderer
ENTRYPOINT ["python3", "mediaTimelineRenderer.py"]

COPY ./ ./


FROM base as test
RUN pytest


FROM base
