import logging
import os
import re

import PIL.Image

from calaldees.files.scan import fast_scan, fast_scan_regex_filter
from calaldees.files.scan_thread import file_scan_diff_thread

from .hachoir import hachoir_metadata
from .renderer_audio import render_audio_to_image
from .renderer_video import render_video_to_image

log = logging.getLogger(__name__)

FILTER_MEDIA_FILE = fast_scan_regex_filter(r'.*(mp4|wav|mp3|ogg)$')


def process_folder(path_media='./', search_filter=FILTER_MEDIA_FILE, **kwargs):
    for file_item in fast_scan(path_media, search_filter=search_filter):
        process_file(file_item, **kwargs)


def watch_folder(**kwargs):
    log.info(f'Watching for changes {kwargs["path_media"]} with interval of {kwargs["daemon_scan_interval_seconds"]} seconds')
    def onchange_function(*args, **kwargs):
        raise NotImplementedError('TODO')
        #process_file(file_item, **kwargs)
    file_scan_diff_thread(
        kwargs['path_media'],
        onchange_function=onchange_function,
        rescan_interval=kwargs['daemon_scan_interval_seconds'],
        search_filter=FILTER_MEDIA_FILE,
    )


def process_file(file_item, **kwargs):
    image_filename = f'{file_item.abspath}.{kwargs["image_format"]}'
    if (
        not kwargs['force']
        and
        os.path.isfile(image_filename)
        and
        file_item.stats.st_mtime == os.path.getmtime(image_filename)
    ):
        log.debug(f'{image_filename} up to date')
        return
    log.info(f'{image_filename} missing or mtime missmatch: Regenerating')
    metadata = hachoir_metadata(file_item.abspath)
    mime_type = metadata.get('mime_type')
    if not re.match(r'(video|audio)', mime_type):
        log.warn(f'unknown mime type {mime_type} {file_item.relative}')
        return
    duration = metadata.get('duration').total_seconds()
    timeline_image = PIL.Image.new('RGB', (int(kwargs['pixels_per_second'] * duration), kwargs['image_height']))
    if 'video' in mime_type:
        render_video_to_image(file_item.abspath, metadata, timeline_image, **kwargs)
    elif 'audio' in mime_type:
        render_audio_to_image(file_item.abspath, metadata, timeline_image, **kwargs)
    timeline_image.save(image_filename)
    os.utime(image_filename, (file_item.stats.st_mtime, file_item.stats.st_mtime))
    # TODO: Future feature: consider scaling down this image for x2 and x4 retina image sourcesets?
