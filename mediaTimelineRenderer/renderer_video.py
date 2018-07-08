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

    rate = 1/(timeline_image.height/PIXELS_PER_SECOND)
    command_ffmpeg = f"""docker run --rm -v {PATH_HOST_MEDIA}:{PATH_HOST_MEDIA}:ro jrottenberg/ffmpeg -loglevel quiet"""

    # Raw video experiment --------------------------------

    def image_generator():
        frame_size_bytes = timeline_image_frame_width * timeline_image.height * 3  # '3' is RGB bytes per pixel
        command_ffmpeg_pipe = f"""{command_ffmpeg} -i "{os.path.join(PATH_HOST_MEDIA, filename)}" -filter:v scale={timeline_image_frame_width}:{timeline_image.height} -r {rate} -vcodec rawvideo -pix_fmt rgb24 -f image2pipe -"""
        with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=2**16, shell=True) as pipe:
            while True:
                image_data = pipe.stdout.read(frame_size_bytes)
                if not image_data:
                    break
                yield Image.frombytes('RGB', (timeline_image_frame_width, timeline_image.height), image_data, 'raw')

    # PNG experiment -----------------------------------------------------------

    def image_png_data_generator():
        BINARY_STREAM_IMAGE_HEADER = b'\x89PNG\r\n\x1a\n'  # bytes(map(int, '137 80 78 71 13 10 26 10'.split(' ')))  # http://www.libpng.org/pub/png/spec/1.2/PNG-Structure.html
        BUFFER_SIZE = 2**16
        command_ffmpeg_pipe = f"""{command_ffmpeg} -i "{os.path.join(PATH_HOST_MEDIA, filename)}" -filter:v scale={timeline_image_frame_width}:{timeline_image.height} -r {rate} -vcodec png -f image2pipe -"""

        image_buffer = BytesIO()
        with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=BUFFER_SIZE, shell=True) as pipe:
            while True:
                data = pipe.stdout.read(BUFFER_SIZE)
                if not data:
                    if image_buffer.tell() > 0:
                        yield image_buffer
                    break
                import pdb ; pdb.set_trace()
                data_split = data.split(BINARY_STREAM_IMAGE_HEADER)
                image_buffer.write(data_split[0])
                for data_split_chunk in data_split[1:]:
                    if image_buffer.tell() > 0:
                        yield image_buffer
                    image_buffer.seek(0)
                    image_buffer.truncate()
                    image_buffer.write(BINARY_STREAM_IMAGE_HEADER)
                    image_buffer.write(data_split_chunk)

    #for index, image in enumerate(map(Image.open, image_png_data_generator())):
    for index, image in enumerate(image_generator()):
        print(image)
        timeline_image.paste(image, (index * timeline_image.height, 0))
