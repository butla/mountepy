"""
Management of Mountebank installation.
Can detect Mountebank installed in the system and also download and setup a standalone distribution
"""

from functools import lru_cache
import logging
import os
import subprocess
import tarfile
import urllib


CACHE_DIR = os.path.expanduser('~/.cache/mountepy')
MB_INSTALL_CHECK_CMD = ['mb', 'help']

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@lru_cache(1)
def get_mb_command():
    """Gets the command to start a Mountebank server in the system.
    Ensures that either Mountebank installation or standalone distribution is available.
    Will trigger Mountebank download if necessary.

    Returns:
        list[str]: Command (Popen-compatible) that starts Mountebank on this system.
    """
    if _check_mb_install():
        return ['mb']
    else:
        if not os.path.exists(CACHE_DIR):
            _setup_standalone()
        mb_dir = _get_mb_dir(CACHE_DIR)
        node_path = _get_node_path(mb_dir)
        mb_exe_path = os.path.join(mb_dir, 'mountebank/bin/mb')
        mb_command = [node_path, mb_exe_path]
        _log.debug('Standalone Mountebank command set to %s', mb_command)
        return mb_command


def _setup_standalone():
    """Downloads and sets up a standalone distribution Mountebank.
    Standalone distribution also contains NodeJS.
    """
    _log.info('Setting up a standalone Mountebank.')
    mb_archive_path, _ = urllib.request.urlretrieve(
        'https://s3.amazonaws.com/mountebank/v1.4/mountebank-v1.4.3-linux-x64.tar.gz')
    mb_tar = tarfile.open(mb_archive_path, mode='r:gz')
    mb_tar.extractall(CACHE_DIR)

    os.remove(mb_archive_path)


def _check_mb_install():
    """Checks if Mountebank is normally installed in the system.

    Returns:
        bool: True if Mountebank is installed, False otherwise.
    """
    try:
        subprocess.check_call(
            MB_INSTALL_CHECK_CMD,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        _log.debug('Detected normal Mountebank installation.')
        return True
    except FileNotFoundError:
        _log.debug('No normal Mountebank installation found.')
        return False


def _get_mb_dir(cache_dir):
    try:
        mb_dir = next(path for path in os.listdir(cache_dir) if path.startswith('mountebank-v'))
        return os.path.join(cache_dir, mb_dir)
    except StopIteration:
        raise MBStandaloneBrokenError(
            "No Mountebank distribution found! "
            "It should have been automatically downloaded earlier")


def _get_node_path(mb_dir):
    try:
        node_path = next(path for path in os.listdir(mb_dir) if path.startswith('node-v'))
        return os.path.join(mb_dir, node_path, 'bin/node')
    except StopIteration:
        raise MBStandaloneBrokenError('No NodeJS distribution found in Mountebank distribution! '
                                      'WTF? Distribution dir: ' + mb_dir)


class MBStandaloneBrokenError(Exception):
    """Means that the standalone Mountebank setup is broken.
    Probably someone deleted some files from it.
    """
