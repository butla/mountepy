import pytest
import shutil

from mountepy import mb_mgmt


def test_local_mb_setup(monkeypatch):
    shutil.rmtree(mb_mgmt.CACHE_DIR, ignore_errors=True)
    monkeypatch.setattr('mountepy.mb_mgmt._check_mb_install', lambda: False)

    mb_command = mb_mgmt.get_mb_command()

    assert len(mb_command) == 2
    assert mb_command[0].endswith('/bin/node')
    assert mb_command[1].endswith('/mountebank/bin/mb')


def test_get_mb_command_mountebank_preinstalled(monkeypatch):
    # substitute mb-checking command with one that succeeds
    monkeypatch.setattr(
        'mountepy.mb_mgmt.MB_INSTALL_CHECK_CMD',
        ['ls'])
    # the path needs to be checked again with the fake command
    mb_mgmt.get_mb_command.cache_clear()
    try:
        assert mb_mgmt.get_mb_command() == ['mb']
    finally:
        # now it needs to be assessed again with real values
        mb_mgmt.get_mb_command.cache_clear()


def test_check_mb_install_false(monkeypatch):
    monkeypatch.setattr(
        'mountepy.mb_mgmt.MB_INSTALL_CHECK_CMD',
        ['asdasdqwerfbvc'])
    assert not mb_mgmt._check_mb_install()


def test_get_mb_dir_error(monkeypatch):
    monkeypatch.setattr('os.listdir', lambda path: ['not', 'mountebank'])
    with pytest.raises(mb_mgmt.MBStandaloneBrokenError):
        mb_mgmt._get_mb_dir('some-fake-path')


def test_get_node_path_error(monkeypatch):
    monkeypatch.setattr('os.listdir', lambda path: ['not', 'node'])
    with pytest.raises(mb_mgmt.MBStandaloneBrokenError):
        mb_mgmt._get_node_path('some-fake-path')