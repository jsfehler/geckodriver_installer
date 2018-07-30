GeckoDriver Installer for Python
=================================
.. image:: https://travis-ci.org/peterhudec/chromedriver_installer.svg?branch=master
    :target: https://travis-ci.org/peterhudec/chromedriver_installer

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

    (e)$ python setup.py install --geckodriver-version=2.10

After install, there should be the ``geckodriver`` executable
available in your path:

.. code-block:: bash

    TODO: Fix this up for geckodriver

    (e)$ which chromedriver
    /home/andypipkin/e/bin/chromedriver
    (e)$ chromedriver --version
    ChromeDriver 2.10.267518
    (e)$ chromedriver
    Starting ChromeDriver (v2.10.267518) on port 9515
    Only local connections are allowed.


Installation With PIP
^^^^^^^^^^^^^^^^^^^^^

The same as before except you need to pass the install options wrapped in pip's
``--install-option=""`` option.

.. code-block:: bash

    (e)$ pip install geckodriver_installer --install-option="--geckodriver-version=2.10"

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
geckodriver version without checksum validation.


Testing
-------

You need `tox <https://testrun.org/tox/latest/>`__ to run the tests.

.. code-block:: bash

    (e)$ git clone https://github.com/tausten/geckodriver_installer.git
    (e)$ pip install -r requirements.txt
    (e)$ tox
