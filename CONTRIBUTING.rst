Contributing
============

Pull requests and issues are welcome.

Pull request requirements
-------------------------

All commit messages need to stick with the `AngularJS commit convention`_
I didn't use it from the project's beginning, but you can look at the log to see some examples.

The project is `versioned semantically`_ (version kept in ``setup.py``),
so the patch number needs to be incremented on every ``fix``, ``perf`` and ``refactor_perf`` commit,
while ``feat`` commits should change the minor version.

After creating a commit, run `Tox`_ to make sure that you did everything OK.

Remember to rebase onto master before submitting your pull request.

Oh, and if you're contributing some documentation (README, docstrings),
it's good to run it through a spell checker (`hunspell`_ is good for command-line usage)

Hints
-----

If you don't have the Python versions required by Tox and you're on Ubuntu, you can install them
from the `Deadsnakes repository`_.

Warnings
--------

Right now there's a `bug in the tests`_, so they can seldom fail or hang.
I'm investigating it right now.
It doesn't appear to affect the tests of software using Mountepy (like my PyDAS project).

If your branch can't fast forward when merging with with master, the automated check
will say that the commit needs to be in AngularJS format, because a merge commit will be created.

.. _AngularJS commit convention: https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit
.. _bug in the tests: https://github.com/butla/mountepy/issues/4
.. _Deadsnakes repository: https://launchpad.net/~fkrull/+archive/ubuntu/deadsnakes
.. _hunspell: https://hunspell.github.io/
.. _Tox: https://tox.readthedocs.io/en/latest/
.. _versioned semantically: http://semver.org/
