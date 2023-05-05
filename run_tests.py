import doctest
import logging
import subprocess
import unittest

import requests

logging.basicConfig(level=logging.DEBUG)


def test():
    test_loader = unittest.defaultTestLoader
    test_runner = unittest.TextTestRunner()
    test_suite = test_loader.discover('.')
    result = test_runner.run(test_suite)

    if not result.wasSuccessful():
        exit(1)


def run_doctest():
    doctest.testfile("README.md", raise_on_error=True, optionflags=doctest.IGNORE_EXCEPTION_DETAIL)


def get_version():
    version = subprocess.check_output(
        ['poetry', 'version', '-s']
    )
    version = version.decode('utf-8')
    version = version.strip()
    logging.debug("Detected version is %s" % (version, ))
    return version


def is_prerelease(version):
    """
        >>> is_prerelease("1.2.4.alpha.2")
        True
        >>> is_prerelease("1.3.0")
        False

    """
    return "alpha" in version or "beta" in version


def check_pypi():
    version = get_version()
    if is_prerelease(version):
        logging.error("Prerelease version on master branch.")
        exit(-2)
    url = "https://pypi.org/project/flask-selfdoc/%s/" % (version, )
    r = requests.get(url)
    if r.status_code == 200:
        logging.error("This version already deployed to pypi")
        exit(-1)
    else:
        exit(0)


def check_pypi_prerelease():
    version = get_version()
    url = "https://pypi.org/project/flask-selfdoc/%s/" % (version, )
    r = requests.get(url)
    if r.status_code == 200:
        logging.error("This version already deployed to pypi")
        exit(-4)
    else:
        if not is_prerelease(version):
            logging.error("Release version on development branch.")
            exit(-3)
        else:
            exit(0)
