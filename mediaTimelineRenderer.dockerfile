FROM python:alpine

RUN pip3 install --upgrade pip setuptools virtualenv
COPY mediaTimelineRenderer.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /mediaTimelineRenderer
ENTRYPOINT ["python3", "mediaTimelineRenderer.py"]
