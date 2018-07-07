FROM docker.io:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt

RUN pip3 install --upgrade pip setuptools virtualenv
COPY mediaTimelineRenderer.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /mediaTimelineRenderer
ENTRYPOINT ["python3", "mediaTimelineRenderer.py"]

# docker build -t mediatimelinerenderer:latest --file .\mediaTimelineRenderer.dockerfile .
# docker run -it --rm -v ../:/mediaTimelineRenderer mediatimelinerenderer:latest