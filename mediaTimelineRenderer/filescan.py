import logging
import os
import re

import PIL.Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
def hachoir_metadata(filename):
    return extractMetadata(createParser(filename))

from calaldees.misc import fast_scan, fast_scan_regex_filter

from .renderer_audio import render_audio_to_image
from .renderer_video import render_video_to_image

log = logging.getLogger(__name__)

FILTER_MEDIA_FILE = fast_scan_regex_filter(r'.*(mp4|wav|mp3|ogg)$')


def process_folder(path_media='./', **kwargs):
    for file_item in fast_scan(path_media, search_filter=FILTER_MEDIA_FILE):
        process_file(file_item, **kwargs)


def process_file(file_item, image_height=64, pixels_per_second=8, image_format='png', **kwargs):
    image_filename = os.path.join(file_item.abspath, f'{file_item.file}.{image_format}')
    if (
        not os.path.isfile(image_filename)
        or
        file_item.stats.mtime != os.path.getmtime(image_filename)
    ):
        log.info(f'${image_filename} missing or mtime missmatch: Regenerating')
        metadata = hachoir_metadata(file_item.abspath)
        mime_type = metadata.get('mime_type')
        if not re.match(r'(video|audio)', mime_type):
            log.warn(f'unknown mime type {mime_type} {file_item.relative}')
            return
        duration = metadata.get('duration').total_seconds()
        image = PIL.Image.new('RGB', (int(pixels_per_second * duration), image_height))
        if 'video' in mime_type:
            image = render_video_to_image(file_item.abspath, image)
        elif 'audio' in mime_type:
            image = render_audio_to_image(file_item.abspath, image)
        image.save(image_filename)
        os.utime(image_filename, (file_item.stats.mtime, file_item.stats.mtime))
        # TODO: Future feature: consider scaling down this image for x2 and x4 retina image sourcesets?
