import subprocess

from PIL import ImageDraw


# https://stackoverflow.com/a/434411/3356840
from itertools import zip_longest
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

from functools import partial
byte_pair_to_short_unsigned_ints = partial(int.from_bytes, byteorder='big')
def bytes_to_short_unsigned_ints(data):
    return map(byte_pair_to_short_unsigned_ints, grouper(data, 2))


def render_audio_to_image(filename, metadata, timeline_image, **kwargs):
    """
    http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
    """
    command_ffmpeg_pipe = f"""{kwargs['command_ffmpeg']} -i "{filename}" -f s16le -acodec pcm_s16le -ac 1 -ar {kwargs['pixels_per_second']} -"""
    # -ar 44100

    # TODO: At the moment we are using the hard pixels per seconds as the audio rate in hz. This is leading to spiking results. We could either get ffmpeg to smooth properly or take in more data and average it

    pixels_to_amplitude_ratio = timeline_image.height / (2**16)
    draw = ImageDraw.Draw(timeline_image)
    def draw_value(x, v):
        amplitude_in_pixels = pixels_to_amplitude_ratio * value
        top = (timeline_image.height - amplitude_in_pixels) / 2
        draw.line((x, top, x, top + amplitude_in_pixels), fill='white', width=1)

    pos = 0
    with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=2**16, shell=True) as pipe:
        while True:
            audio_data = pipe.stdout.read()
            if not audio_data:
                break
            for value in bytes_to_short_unsigned_ints(audio_data):
                draw_value(pos, value)
                pos += 1
