import logging
import os
import subprocess
from io import BytesIO

from PIL import Image, ImageSequence

log = logging.getLogger(__name__)


def render_video_to_image(filename, metadata, timeline_image, **kwargs):
    """
    http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
    """
    log.debug(f'Rendering video - {filename}')

    timeline_image_frame_width = int((metadata.get('width')/metadata.get('height')) * timeline_image.height)
    rate = 1/(timeline_image.height/kwargs['pixels_per_second'])

    def image_generator():
        frame_size_bytes = timeline_image_frame_width * timeline_image.height * 3  # '3' is RGB bytes per pixel rgb24
        command_ffmpeg_pipe = f"""{kwargs['command_ffmpeg']} -i "{filename}" -filter:v scale={timeline_image_frame_width}:{timeline_image.height} -r {rate} -vcodec rawvideo -pix_fmt rgb24 -f image2pipe -"""
        log.debug(command_ffmpeg_pipe)
        with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=2**16, shell=True) as pipe:
            while True:
                image_data = pipe.stdout.read(frame_size_bytes)
                if not image_data:
                    break
                yield Image.frombytes('RGB', (timeline_image_frame_width, timeline_image.height), image_data, 'raw')

    for index, image in enumerate(image_generator()):
        # ffmpeg seems to duplicate the first frame. Using `index-1` solves this
        timeline_image.paste(image, ((index-1) * timeline_image.height, 0))
