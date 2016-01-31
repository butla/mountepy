import pytest
import shutil

from mountepy.mb_mgmt import _MountebankInstallManager, MBStandaloneBrokenError

@pytest.fixture
def mb_mgr():
    return _MountebankInstallManager()


def test_local_mb_setup(mb_mgr):
    shutil.rmtree(_MountebankInstallManager.CACHE_DIR, ignore_errors=True)
    mb_mgr._check_mb_install = lambda: False

    mb_command = mb_mgr.get_mb_command()

    assert len(mb_command) == 2
    assert mb_command[0].endswith('/bin/node')
    assert mb_command[1].endswith('/mountebank/bin/mb')


def test_check_mb_install_true(mb_mgr, monkeypatch):
    monkeypatch.setattr(
        'mountepy.mb_mgmt._MountebankInstallManager.MB_INSTALL_CHECK_CMD',
        ['ls'])
    assert mb_mgr._check_mb_install()


def test_check_mb_install_false(mb_mgr, monkeypatch):
    monkeypatch.setattr(
        'mountepy.mb_mgmt._MountebankInstallManager.MB_INSTALL_CHECK_CMD',
        ['asdasdqwerfbvc'])
    assert not mb_mgr._check_mb_install()


def test_get_mb_dir_error(mb_mgr, monkeypatch):
    monkeypatch.setattr('os.listdir', lambda path: ['not', 'mountebank'])
    with pytest.raises(MBStandaloneBrokenError):
        mb_mgr._get_mb_dir('some-fake-path')


def test_get_node_path_error(mb_mgr, monkeypatch):
    monkeypatch.setattr('os.listdir', lambda path: ['not', 'node'])
    with pytest.raises(MBStandaloneBrokenError):
        mb_mgr._get_node_path('some-fake-path')