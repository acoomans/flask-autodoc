import unittest

from flask import Flask
from flask_selfdoc import Autodoc


class TestErrorHandling(unittest.TestCase):
    def test_app_not_initialized(self):
        app = Flask(__name__)
        autodoc = Autodoc()
        with app.app_context():
            self.assertRaises(RuntimeError, lambda: autodoc.html())

    def test_app_initialized_by_ctor(self):
        app = Flask(__name__)
        autodoc = Autodoc(app)
        with app.app_context():
            autodoc.html()

    def test_app_initialized_by_init_app(self):
        app = Flask(__name__)
        autodoc = Autodoc()
        autodoc.init_app(app)
        with app.app_context():
            autodoc.html()
