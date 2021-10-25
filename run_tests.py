import doctest
import os
import subprocess


def test():
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover']
    )


def run_doctest():
    doctest.testfile("README.md")
