import itertools
import os
import re
import shlex
import subprocess
import tempfile
from distutils.version import StrictVersion

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import pytest

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
VIRTUALENV_DIR = os.environ['VIRTUAL_ENV']
INSTALL_COMMAND_BASE = 'pip install {0} '.format(PROJECT_DIR)
OLDEST_SUPPORTED_VERSION = '0.11.1'


def generate_version_fixture_params():
    """
    Loads all known versions of geckodriver from
    `https://github.com/mozilla/geckodriver/releases`__
    and returns a dictionary with keys ``params`` and ``ids`` which should be
    unpacked as arguments to :func:`pytest.fixture` decorator.

    This way we can generate and ``params`` and ``ids`` arguments with a single
    function call. We need the ``ids`` parameter for nice display of tested
    versions in the verbose ``pytest`` output.

    :returns:
        A dictionary with keys ``params`` and ``ids``.
    """
    body = urlopen('https://api.github.com/repos/mozilla/geckodriver/releases').read()
    versions = re.findall(
        r'\"tag_name\":\s?\"v(\d+\.\d+\.\d+)\"()',
        body.decode('utf-8'),
    )

    versions = [pair for pair in versions if StrictVersion(pair[0]) >= StrictVersion(OLDEST_SUPPORTED_VERSION)]

    params = [
        (ver, [checksum for _, checksum in checksums])
        for ver, checksums in itertools.groupby(versions, lambda x: x[0])
    ]

    return dict(
        params=params,
        ids=[version for version, _ in params]
    )


@pytest.fixture(**generate_version_fixture_params())
def version(request):
    request.param_index = request.param[0]
    return request.param


class Base(object):
    def _uninstall(self):
        try:
            subprocess.check_call(
                self._get_popen_args('pip uninstall geckodriver_installer -y')
            )
        except subprocess.CalledProcessError:
            pass

        geckodriver_executable = os.path.join(VIRTUALENV_DIR,
                                               'bin', 'geckodriver')

        if os.path.exists(geckodriver_executable):
            print('REMOVING geckodriver executable: ' +
                  geckodriver_executable)
            os.remove(geckodriver_executable)

    def teardown(self):
        self._uninstall()

    def _not_available(self):
        with pytest.raises(OSError):
            subprocess.check_call(self._get_popen_args('geckodriver --version'))

    def _get_popen_args(self, command):
        if os.name == 'posix':
            return shlex.split(command, posix=os.name == 'posix')
        else:
            return command


class VersionBase(Base):
    def _assert_cached_files_exist(self, exists, remove=False):
        path = os.path.join(tempfile.gettempdir(),
                            'geckodriver_{0}.zip'.format(self.version))

        if remove and os.path.exists(path):
            os.remove(path)

        assert os.path.exists(path) is exists

    def _test_version(self, version, cached):
        self.version, self.checksums = version

        # geckodriver executable should not be available.
        self._not_available()

        # Assert that zip archives are cached or not, depending on test type.
        self._assert_cached_files_exist(cached, remove=not cached)

        # After installation...
        subprocess.check_call(self._get_popen_args(self._get_install_command()))

        # ...the geckodriver executable should be available...
        expected_version, error = subprocess.Popen(
            self._get_popen_args('geckodriver --version'),
            stdout=subprocess.PIPE
        ).communicate()

        # ...and should be of the right version.
        assert self.version in str(expected_version)

    def test_version_uncached(self, version):
        self._test_version(version, cached=False)


class TestVersionOnly(VersionBase):
    def _get_install_command(self):
        return (
            INSTALL_COMMAND_BASE +
            '--install-option="--geckodriver-version={0}"'.format(self.version)
        )

    def test_version_cached(self, version):
        self._test_version(version, cached=True)
