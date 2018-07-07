import logging
import os
import subprocess
from io import BytesIO

from PIL import Image, ImageSequence

from .hachoir import hachoir_metadata

log = logging.getLogger(__name__)

def render_video_to_image(filename, timeline_image):
    PIXELS_PER_SECOND = 8
    BINARY_STREAM_IMAGE_HEADER = b'\xff\xd8\xff\xe0'  # \x00\x10JFIF

    PATH_HOST_MEDIA = os.getenv('PATH_HOST_MEDIA')  # TODO: replace this as part of kwargs?

    rate = 1/(timeline_image.height/PIXELS_PER_SECOND)
    command_ffmpeg = f'docker run --rm -it -v {PATH_HOST_MEDIA}:{PATH_HOST_MEDIA}:ro jrottenberg/ffmpeg'
    command_ffmpeg_pipe = f'{command_ffmpeg} -loglevel quiet -i "{os.path.join(PATH_HOST_MEDIA, filename)}" -r {rate} -f image2pipe -'

    def add_image_to_timeline(image_buffer, image_sequence_number):
        if image_buffer.tell() == 0:
            return
        image_buffer.seek(0)
        try:
            i = Image.open(image_buffer)
            # Resize the image to add to our timeline image
            aspect_ratio = i.width/i.height
            #i.resize((int(i.width * aspect_ratio * timeline_image.height), timeline_image.height))
            i.thumbnail((int(i.width * aspect_ratio * timeline_image.height), timeline_image.height), Image.ANTIALIAS)
            print(i)
            # Compose image on timeline image
            timeline_image.paste(i, (image_sequence_number * timeline_image.height, 0))
        except Exception as e:
            log.warn('image loading error')
            return

    BUFFER_SIZE = 2**16
    image_sequence_number = 0
    image_buffer = BytesIO()
    with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=BUFFER_SIZE, shell=True) as pipe:
        while True:
            data = pipe.stdout.read(BUFFER_SIZE)
            if not data:
                break
            data_split = data.split(BINARY_STREAM_IMAGE_HEADER)
            image_buffer.write(data_split[0])
            for data_split_chunk in data_split[1:]:
                add_image_to_timeline(image_buffer, image_sequence_number)
                image_sequence_number += 1
                image_buffer.seek(0)
                image_buffer.truncate()
                image_buffer.write(BINARY_STREAM_IMAGE_HEADER)
                image_buffer.write(data_split_chunk)
    add_image_to_timeline(image_buffer, image_sequence_number)
