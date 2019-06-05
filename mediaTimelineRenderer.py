import os
import json
import logging

from calaldees.debug import postmortem

VERSION = 'v0.0.0'

log = logging.getLogger(__name__)


# Constants --------------------------------------------------------------------

DESCRIPTION = """
    mediaTimelineRenderer
"""

DEFAULT_CONFIG_FILENAME = 'config.json'


# Command Line Arguments -------------------------------------------------------

def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description=DESCRIPTION,
    )

    parser.add_argument('path_media', action='store', help='', default='./')

    parser.add_argument('--daemon_scan_interval_seconds', type=int, action='store', help='', default=0)

    parser.add_argument('--image_format', action='store', help='', default='png')
    parser.add_argument('--image_height', type=int, action='store', help='', default=64)
    parser.add_argument('--pixels_per_second', type=int, action='store', help='The number of horizontal pixels that represent a second', default=8)
    parser.add_argument('--command_ffmpeg', action='store', help='', default='ffmpeg -loglevel quiet')

    parser.add_argument('--force', action='store_true', help='ignore file mtimes and regenerate all timelines', default=False)

    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)

    parser.add_argument('--vscode_debugger_port', type=int, action='store', help='attach to vscode')
    parser.add_argument('--postmortem', action='store', help='Enter debugger on exception')
    parser.add_argument('--log_level', type=int, help='log level', default=logging.INFO)

    parser.add_argument('--version', action='version', version=VERSION)

    kwargs = vars(parser.parse_args())

    # Overlay config defaults from file
    if os.path.isfile(kwargs['config']):
        with open(kwargs['config'], 'rt') as config_filehandle:
            config = json.load(config_filehandle)
            kwargs = {k: v if v is not None else config.get(k) for k, v in kwargs.items()}
            kwargs.update({k: v for k, v in config.items() if k not in kwargs})

    # Format strings
    for key, value in kwargs.items():
        if isinstance(value, str):
            kwargs[key] = value.format(**kwargs)

    return kwargs


# Main -------------------------------------------------------------------------

def main(**kwargs):
    from mediaTimelineRendererLib.filescan import process_folder, watch_folder
    process_folder(**kwargs)
    if kwargs['daemon_scan_interval_seconds']:
        watch_folder(**kwargs)

if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    if kwargs.get('vscode_debugger_port'):
        import ptvsd
        ptvsd.enable_attach("my_secret", address=('0.0.0.0', kwargs.get('vscode_debugger_port')))
        #ptvsd.wait_for_attach()

    def launch():
        main(**kwargs)
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
