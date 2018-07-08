import logging
import os
import subprocess
from io import BytesIO

from PIL import Image, ImageSequence

from .hachoir import hachoir_metadata

log = logging.getLogger(__name__)


def render_video_to_image(filename, timeline_image):
    PIXELS_PER_SECOND = 8

    PATH_HOST_MEDIA = os.getenv('PATH_HOST_MEDIA')  # TODO: replace this as part of kwargs?

    metadata = hachoir_metadata(filename)
    width = metadata.get('width')
    height = metadata.get('height')
    timeline_image_frame_width = int((width/height) * timeline_image.height)
    frame_size_bytes = timeline_image_frame_width * timeline_image.height * 3  # '3' is RGB bytes per pixel

    rate = 1/(timeline_image.height/PIXELS_PER_SECOND)
    command_ffmpeg = f"""docker run --rm -it -v {PATH_HOST_MEDIA}:{PATH_HOST_MEDIA}:ro jrottenberg/ffmpeg -loglevel quiet"""
    command_ffmpeg_pipe = f"""{command_ffmpeg} -i "{os.path.join(PATH_HOST_MEDIA, filename)}" -filter:v scale={timeline_image_frame_width}:{timeline_image.height} -r {rate} -vcodec rawvideo -pix_fmt rgb24 -f image2pipe -"""
# -vframes 1

    def image_generator():
        with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=2**16, shell=True) as pipe:
            while True:
                image_data = pipe.stdout.read(frame_size_bytes)
                if not image_data or len(image_data) != frame_size_bytes: # this was a sign, the frame sizez were not even
                    break
                #print(len(image_data)) # the byte length dont match for -vframes 1
                #print(frame_size_bytes)
                yield Image.frombytes('RGB', (timeline_image_frame_width, timeline_image.height), image_data, 'raw')  # timeline_image.height

    for index, image in enumerate(image_generator()):
        print(image)
        timeline_image.paste(image, (index * timeline_image.height, 0))
