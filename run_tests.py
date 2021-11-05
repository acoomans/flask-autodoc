import doctest
import logging
import os
import subprocess

import requests

logging.basicConfig(level=logging.DEBUG)


def test():
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover']
    )


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


def check_pypi():
    version = get_version()
    url = "https://pypi.org/project/flask-selfdoc/%s/" % (version, )
    r = requests.get(url)
    if r.status_code == 200:
        exit(-1)
    else:
        exit(0)
