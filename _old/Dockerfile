FROM python:alpine

# Install docker + docker-compose on alpine
# https://github.com/docker-library/docker/blob/master/18.06/Dockerfile
# https://github.com/tmaier/docker-compose/blob/master/Dockerfile
COPY --from=docker /usr/local/bin/docker* /usr/local/bin/
COPY --from=docker /usr/local/bin/modprobe /usr/local/bin/modprobe
#RUN pip3 install --no-cache-dir "docker-compose"

RUN apk add --no-cache jpeg-dev zlib-dev
COPY mediaTimelineRenderer.pip requirements.pip
RUN apk add --no-cache \
        --virtual .build-deps build-base linux-headers git &&\
    pip3 install --no-cache-dir -r requirements.pip &&\
    apk del .build-deps

WORKDIR /mediaTimelineRenderer
ENTRYPOINT ["python3", "mediaTimelineRenderer.py"]

COPY ./ ./

# docker build -t mediatimelinerenderer:latest --file .\mediaTimelineRenderer.dockerfile .
# docker run -it --rm -v ../:/mediaTimelineRenderer mediatimelinerenderer:latest
