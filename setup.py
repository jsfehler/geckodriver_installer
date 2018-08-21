from setuptools.command.install import install
from setuptools.command.develop import develop
from distutils.command.build_scripts import build_scripts
from setuptools import setup
from distutils.version import StrictVersion
import os
import platform
import re
import tempfile
import sys
import zipfile
import tarfile

try:
    from urllib import request
except ImportError:
    import urllib as request


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, 'r') as f:
        return f.read()


GECKODRIVER_INFO_URL = (
    'https://api.github.com/repos/mozilla/geckodriver/releases'
)
GECKODRIVER_URL_TEMPLATE = (
    'https://github.com/mozilla/geckodriver/releases/download/v{version}/'
    'geckodriver-v{version}-{os_}{architecture}.{compression}'
)

GECKODRIVER_RELEASES_VERSION_PATTERN = re.compile(r'\"tag_name\":\s?\"v(\d+\.\d+\.\d+)\"')
GECKODRIVER_VERSION_PATTERN = re.compile(r'(\d+\.\d+\.\d+)')

OLDEST_SUPPORTED_VERSION = '0.11.1'

# Global variables
geckodriver_version = None


def get_geckodriver_version():
    """Retrieves the most recent geckodriver version."""
    global geckodriver_version

    response = request.urlopen(GECKODRIVER_INFO_URL)
    content = response.read()
    match = GECKODRIVER_RELEASES_VERSION_PATTERN.search(str(content))
    if match:
        return match.group(1)
    else:
        raise Exception('Unable to get latest geckodriver version from {0}'
                        .format(GECKODRIVER_INFO_URL))


class GeckoInstaller:
    def __init__(self, build_dir):
        self.build_dir = build_dir

    def _unzip(self, zip_path):
        if zip_path.endswith('zip'):
            zf = zipfile.ZipFile(zip_path)
        else:
            zf = tarfile.open(zip_path)

        print("\t - extracting '{0}' to '{1}'."
              .format(zip_path, self.build_dir))
        zf.extractall(self.build_dir)

    def _get_compression_suffix(self):
        result = 'tar.gz'
        if platform.platform().lower().startswith('win'):
            result = 'zip'
        return result

    def _download(self, zip_path):
        compression = 'tar.gz'
        architecture = platform.architecture()[0][:-3]
        plat = platform.platform().lower()
        if plat.startswith('darwin'):
            os_ = 'macos'
            # Only 64 bit architecture is available for mac since version 2.23
            architecture = ''
        elif plat.startswith('linux'):
            os_ = 'linux'
        elif plat.startswith('win'):
            os_ = 'win'
            compression = 'zip'
        else:
            raise Exception('Unsupported platform: {0}'.format(plat))

        url = GECKODRIVER_URL_TEMPLATE.format(version=geckodriver_version,
                                               os_=os_,
                                               architecture=architecture,
                                               compression=compression)

        download_report_template = ("\t - downloading from '{0}' to '{1}'"
                                    .format(url, zip_path))

        def reporthoook(x, y, z):
            global download_ok

            percent_downloaded = '{0:.0%}'.format((x * y) / float(z))
            sys.stdout.write('\r')
            sys.stdout.write("{0} [{1}]".format(download_report_template,
                                                percent_downloaded))
            download_ok =  percent_downloaded == '100%'
            if download_ok:
                sys.stdout.write(' OK')
            sys.stdout.flush()

        request.urlretrieve(url, zip_path, reporthoook)

        print('')
        if not download_ok:
            print('\t - download failed!')


class BuildScripts(build_scripts):
    """Downloads and unzips the requested geckodriver executable."""
    def run(self):
        global geckodriver_version, geckodriver_checksums

        if not geckodriver_version:
            geckodriver_version = get_geckodriver_version()

        gecko_installer = GeckoInstaller(self.build_dir)

        file_name = 'geckodriver_{version}.{compression}'.format(version=geckodriver_version, compression=gecko_installer._get_compression_suffix())
        zip_path = os.path.join(tempfile.gettempdir(), file_name)


        gecko_installer._download(zip_path)
        gecko_installer._unzip(zip_path)

        self.scripts = [os.path.join(self.build_dir, script) for script in
                        os.listdir(self.build_dir)]
        build_scripts.run(self)
        self.copy_scripts()

    def finalize_options(self):
        build_scripts.finalize_options(self)
        self.initialize_options()
        self.set_undefined_options('build', ('build_scripts', 'build_dir'))
        self.run()

        #self.scripts = []


class Install(install):
    """Used to get geckodriver version and checksums from install options"""

    # Fix an error when pip calls setup.py with the
    # --single-version-externally-managed and it is not supported due to
    # old setuptools version.
    _svem = list(filter(lambda x: x[0] == 'single-version-externally-managed',
                        install.user_options))

    if not _svem:
        single_version_externally_managed = None
        install.user_options.append(('single-version-externally-managed',
                                     None, ""))

    user_options = install.user_options + [
        ('geckodriver-version=', None, 'Geckodriver version'),
        ('geckodriver-checksums=', None, 'Geckodriver checksums'),
    ]

    def initialize_options(self):
        self.geckodriver_version = None
        install.initialize_options(self)

    def run(self):
        global geckodriver_version

        if self.geckodriver_version:
            if not GECKODRIVER_VERSION_PATTERN.match(self.geckodriver_version):
                raise Exception('Invalid --geckodriver-version={0}! '
                                'Must match /{1}/'
                                .format(self.geckodriver_version,
                                        GECKODRIVER_VERSION_PATTERN.pattern))

            if not StrictVersion(self.geckodriver_version) >= StrictVersion(OLDEST_SUPPORTED_VERSION):
                raise Exception('Invalid --geckodriver-version={0}! '
                                'Minimum supported version is {1}'
                                .format(self.geckodriver_version,
                                        OLDEST_SUPPORTED_VERSION))

        geckodriver_version = self.geckodriver_version

        install.run(self)


class PostDevelop(develop):
    """Used to get geckodriver version and checksums from install options"""

    # Fix an error when pip calls setup.py with the
    # --single-version-externally-managed and it is not supported due to
    # old setuptools version.
    _svem = list(filter(lambda x: x[0] == 'single-version-externally-managed',
                        develop.user_options))

    if not _svem:
        single_version_externally_managed = None
        develop.user_options.append(('single-version-externally-managed',
                                     None, ""))

    user_options = develop.user_options + [
        ('geckodriver-version=', None, 'Geckodriver version'),
        ('geckodriver-checksums=', None, 'Geckodriver checksums'),
    ]

    def initialize_options(self):
        self.geckodriver_version = None
        develop.initialize_options(self)

    def run(self):
        global geckodriver_version

        if self.geckodriver_version:
            if not GECKODRIVER_VERSION_PATTERN.match(self.geckodriver_version):
                raise Exception('Invalid --geckodriver-version={0}! '
                                'Must match /{1}/'
                                .format(self.geckodriver_version,
                                        GECKODRIVER_VERSION_PATTERN.pattern))

            if not StrictVersion(self.geckodriver_version) >= StrictVersion(OLDEST_SUPPORTED_VERSION):
                raise Exception('Invalid --geckodriver-version={0}! '
                                'Minimum supported version is {1}'
                                .format(self.geckodriver_version,
                                        OLDEST_SUPPORTED_VERSION))

        geckodriver_version = self.geckodriver_version

        develop.run(self)


setup(
    name='geckodriver_installer',
    version='0.0.2',
    author='Tyler Austen',
    author_email='tyler@springahead.com',
    description='Geckodriver Installer',
    long_description=read('README.rst'),
    keywords='geckodriver installer',
    url='https://github.com/tausten/geckodriver_installer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Installation/Setup',
    ],
    license='MIT',
    package_data={'': ['*.txt', '*.rst']},
    # If packages is empty, contents of ./build/lib will not be copied!
    packages=['geckodriver_installer'],
    scripts=['blank.py'],
    cmdclass=dict(build_scripts=BuildScripts, install=Install, develop=PostDevelop)
)
