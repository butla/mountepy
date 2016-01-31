"""
Management of Mountebank installation.
"""

import logging
import os
import subprocess
import tarfile
import urllib


_mb_command = None


def get_mb_command():
    global _mb_command
    if not _mb_command:
        _mb_command = _MountebankInstallManager().get_mb_command()

    return _mb_command


class MBStandaloneBrokenError(Exception):
    """
    Means that the standalone Mountebank setup is broken.
    Probably someone deleted some files from it.
    """
    pass


class _MountebankInstallManager:

    """
    Manages installation of Mountebank.
    Can detect Mountebank installed in the system.
    Can also download and setup a standalone distribution.
    """

    CACHE_DIR = os.path.expanduser('~/.cache/mountepy')
    MB_INSTALL_CHECK_CMD = ['mb', 'help']

    def __init__(self):
        self._log = logging.getLogger(__name__)

    def get_mb_command(self):
        """
        Gets the command to start a Mountebank server in the system.
        Ensures that either Mountebank installation or standalone distribution is available.
        Will trigger Mountebank download if necessary.
        :returns: The command that can be used to start Mountebank server.
        :rtype: list[str]
        """
        if self._check_mb_install(): # pragma: no cover
            mb_command = ['mb']
        else:
            if not os.path.exists(self.CACHE_DIR):
                self._setup_standalone()
            mb_dir = self._get_mb_dir(self.CACHE_DIR)
            node_path = self._get_node_path(mb_dir)
            mb_exe_path = os.path.join(mb_dir, 'mountebank/bin/mb')
            mb_command = [node_path, mb_exe_path]
            self._log.debug('Standalone Mountebank command set to %s', mb_command)
        return mb_command

    def _setup_standalone(self):
        """
        Downloads and sets up a standalone distribution Mountebank.
        Standalone distribution also contains NodeJS.
        """
        self._log.info('Setting up a standalone Mountebank.')
        mb_archive_path, _ = urllib.request.urlretrieve(
            'https://s3.amazonaws.com/mountebank/v1.4/mountebank-v1.4.3-linux-x64.tar.gz')
        mb_tar = tarfile.open(mb_archive_path, mode='r:gz')
        mb_tar.extractall(self.CACHE_DIR)

        os.remove(mb_archive_path)

    def _check_mb_install(self):
        """
        Checks if Mountebank is normally installed in the system.
        :return: True if Mountebank is installed, False otherwise.
        :rtype: bool
        """
        try:
            subprocess.check_call(
                self.MB_INSTALL_CHECK_CMD,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            self._log.debug('Detected normal Mountebank installation.')
            return True
        except FileNotFoundError:
            self._log.debug('No normal Mountebank installation found.')
            return False

    @staticmethod
    def _get_mb_dir(cache_dir):
        try:
            mb_dir = next(path for path in os.listdir(cache_dir) if path.startswith('mountebank-v'))
            return os.path.join(cache_dir, mb_dir)
        except StopIteration:
            raise MBStandaloneBrokenError(
                "No Mountebank distribution found! "
                "It should have been automatically downloaded earlier")

    @staticmethod
    def _get_node_path(mb_dir):
        try:
            node_path = next(path for path in os.listdir(mb_dir) if path.startswith('node-v'))
            return os.path.join(mb_dir, node_path, 'bin/node')
        except StopIteration:
            raise MBStandaloneBrokenError(
                'No NodeJS distribution found in Mountebank distribution! WTF? Distribution dir: '
                + mb_dir)
