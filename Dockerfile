FROM python:alpine as base

COPY --from=jrottenberg/ffmpeg /usr/local /usr/local

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
