import os
import shutil
import subprocess
import uuid

import pytest

REPO_DIR = 'repodir'
BUILD_CODE_OUT = b'build_code'
BUILD_DOCS_OUT = b'build_docs'


@pytest.yield_fixture
def repo():
    subprocess.check_call(['git', 'init', REPO_DIR])
    os.chdir(REPO_DIR)

    _create_commit('Initial commit')
    yield
    os.chdir('..')
    shutil.rmtree(REPO_DIR)


@pytest.mark.parametrize('commit_message, action', [
    ('feat(something): Added some feature.', BUILD_CODE_OUT),
    ('fix(something): Fixed some code.', BUILD_CODE_OUT),
    ('refactor(something): Refactored some code.', BUILD_CODE_OUT),
    ('perf(something): Increased performance somewhere.', BUILD_CODE_OUT),
    ('docs(something): Changed the readme.', BUILD_DOCS_OUT),
    ('style(something): Changed styling somewhere.', BUILD_DOCS_OUT),
    ('test(something): Refactored some tests.', BUILD_DOCS_OUT),
    ('chore(something): Did some CI stuff.', BUILD_DOCS_OUT),
])
def test_get_commit_action_for_proper_commit(repo, commit_message, action):
    _create_commit(commit_message)
    assert _get_commit_action() == action


def test_get_commit_action_for_invalid_commit(repo):
    _create_commit('fix of something')
    with pytest.raises(subprocess.CalledProcessError):
        _get_commit_action()


def _create_commit(message):
    file_name = str(uuid.uuid4())
    subprocess.check_call(['touch', file_name])
    subprocess.check_call(['git', 'add', file_name])
    subprocess.check_call(['git', 'commit', '-am', message])


def _get_commit_action():
    return subprocess.check_output('../get_commit_action.sh')

