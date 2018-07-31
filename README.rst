GeckoDriver Installer for Python
=================================
Adapted from https://github.com/authomatic/chromedriver_installer

Installs `GeckoDriver executable <https://github.com/mozilla/geckodriver/releases>`__
with **pip** or **setup.py**.

Usage
-----

Manual Installation
^^^^^^^^^^^^^^^^^^^

Clone the repository:

.. code-block:: bash

    (e)$ git clone https://github.com/tausten/geckodriver_installer.git

Install the most recent **GeckoDriver** version

.. code-block:: bash

    (e)$ python setup.py install

Install specific **GeckoDriver** version

.. code-block:: bash

    (e)$ python setup.py install --geckodriver-version=0.21.0

After install, there should be the ``geckodriver`` executable
available in your path:

.. code-block:: bash

    (e)$ which geckodriver
    /home/andypipkin/e/bin/geckodriver
    (e)$ geckodriver --version
    geckodriver 0.21.0
    (e)$ geckodriver
    1532996000606   geckodriver     INFO    geckodriver 0.21.0
    1532996000617   geckodriver     INFO    Listening on 127.0.0.1:4444

Installation With PIP
^^^^^^^^^^^^^^^^^^^^^

The same as before except you need to pass the install options wrapped in pip's
``--install-option=""`` option.

.. code-block:: bash

    (e)$ pip install geckodriver_installer --install-option="--geckodriver-version=0.21.0"

Installation With easy_install
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I can't seem to find a way to make **easy_install** pass *user options* to
**setup.py** so you only can install the most recent
**GeckoDriver** version with **easy_install**.

How it Works
------------

The **build_scripts** command of the **setup.py** script invoked by
``python setup.py install`` downloads, the **GeckoDriver** zip archive version
specified in the ``--geckodriver-version`` option from
https://github.com/mozilla/geckodriver/releases
to the **temp** directory of the operating system.
The archive will be unzipped to the *build directory* and installed
as an executable to the *bin directory*.

If the ``--geckodriver-version`` option is ommited, it installs the most recent
geckodriver version.


Testing
-------

You need `tox <https://testrun.org/tox/latest/>`__ to run the tests.

.. code-block:: bash

    (e)$ git clone https://github.com/tausten/geckodriver_installer.git
    (e)$ tox
