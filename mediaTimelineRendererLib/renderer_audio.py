import logging
import subprocess
import statistics

from PIL import ImageDraw

from calaldees.data import grouper

log = logging.getLogger(__name__)


from functools import partial
byte_pair_to_short_unsigned_ints = partial(int.from_bytes, byteorder='big')
def bytes_to_short_unsigned_ints(data):
    return map(byte_pair_to_short_unsigned_ints, grouper(data, 2))


def render_audio_to_image(filename, metadata, timeline_image, pixels_per_second=8, audio_input_samples_per_pixel=32, **kwargs):
    """
    http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
    """
    log.debug(f'Rendering audio - {filename}')
    command_ffmpeg_pipe = f"""{kwargs['command_ffmpeg']} -i "{filename}" -f s16le -acodec pcm_s16le -ac 1 -ar {pixels_per_second * audio_input_samples_per_pixel} -"""
    # -ar 44100
    log.debug(command_ffmpeg_pipe)

    # TODO: At the moment we are using the hard pixels per seconds as the audio rate in hz. This is leading to spiking results. We could either get ffmpeg to smooth properly or take in more data and average it

    pixels_to_amplitude_ratio = timeline_image.height / (2**16)
    draw = ImageDraw.Draw(timeline_image)
    def _draw_amplitude(x, v, color='white'):
        amplitude_in_pixels = pixels_to_amplitude_ratio * v
        top = (timeline_image.height - amplitude_in_pixels) / 2
        draw.line((x, top, x, top + amplitude_in_pixels), fill=color, width=1)
    def _draw_values(x, values):
        values_mean = statistics.mean(values)
        values_max = max(values)
        q1 = values[int(audio_input_samples_per_pixel * 0.25)]
        q3 = values[int(audio_input_samples_per_pixel * 0.75)]
        #values_variance = statistics.variance(values, xbar=values_mean)
        _draw_amplitude(x, q3, (128,)*3)
        _draw_amplitude(x, values_mean, (198,)*3)
        _draw_amplitude(x, q1, (255,)*3)

    pos = 0
    with subprocess.Popen(command_ffmpeg_pipe, stdout=subprocess.PIPE, bufsize=2**16, shell=True) as pipe:
        while True:
            audio_data = pipe.stdout.read()
            if not audio_data:
                break
            for values in grouper(bytes_to_short_unsigned_ints(audio_data), audio_input_samples_per_pixel, 0):
                _draw_values(pos, sorted(values))
                pos += 1
