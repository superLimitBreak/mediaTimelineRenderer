import logging
import json

from calaldees.misc import postmortem

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

    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)

    parser.add_argument('--vscode_debugger', action='store', help='attach to vscode')
    parser.add_argument('--postmortem', action='store', help='Enter debugger on exception')
    parser.add_argument('--log_level', type=int, help='log level')

    parser.add_argument('--version', action='version', version=VERSION)

    kwargs = vars(parser.parse_args())

    # Overlay config defaults from file
    with open(kwargs['config'], 'rt') as config_filehandle:
        config = json.load(config_filehandle)
        kwargs = {k: v if v is not None else config.get(k) for k, v in kwargs.items()}
        kwargs.update({k: v for k, v in config.items() if k not in kwargs})

    return kwargs


# Main -------------------------------------------------------------------------

def main(**kwargs):
    from mediaTimelineRenderer.filescan import process_folder
    process_folder(kwargs['path_media'])


if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    if kwargs.get('vscode_debugger'):
        import ptvsd
        ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3000))
        #ptvsd.wait_for_attach()

    def launch():
        main(**kwargs)
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
