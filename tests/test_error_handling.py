import unittest

from flask import Flask
from flask_autodoc import Autodoc


class TestErrorHandling(unittest.TestCase):
    def test_app_not_initialized(self):
        app = Flask(__name__)
        app.debug = True
        autodoc = Autodoc()
        with app.app_context():
            self.assertRaises(RuntimeError, lambda: autodoc.html())
