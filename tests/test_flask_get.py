import json
import unittest

from flask import Flask, current_app
from flask_selfdoc import Autodoc


class TestAutodocWithFlask(unittest.TestCase):
    def setup_app(self):
        self.app = Flask(__name__)
        self.autodoc = Autodoc(self.app)

    def setUp(self):
        self.setup_app()

        @self.app.route('/')
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return 'Hello World!'

        self.client = self.app.test_client()

    def test_html(self):
        @self.app.route('/docs')
        def html_docs():
            return self.autodoc.html()

        response = self.client.get('/docs')
        self.assertEqual(response.status_code, 200)

    def test_json(self):
        @self.app.route('/docs')
        def json_docs():
            return self.autodoc.json()

        response = self.client.get('/docs')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('endpoints', data)
        self.assertEqual(len(data['endpoints']), 1)

        endpoint = data['endpoints'][0]
        expected = {
            "args": [],
            "docstring": "Returns a hello world message",
            "methods": ["GET", "HEAD", "OPTIONS"],
            "rule": "/"
        }
        self.assertEqual(endpoint, expected)


class TestAutodocWithFlaskFactory(TestAutodocWithFlask):
    def setup_app(self):
        self.app = Flask(__name__)
        self.autodoc = Autodoc()
        self.autodoc.init_app(self.app)


class TestAutodocTwoApps(unittest.TestCase):
    def setUp(self):
        self.app_1 = Flask(__name__)
        self.app_2 = Flask(__name__)
        self.autodoc = Autodoc()
        self.autodoc.init_app(self.app_1)
        self.autodoc.init_app(self.app_2)

    def test_endpoint_on_one_app(self):
        @self.app_1.route('/')
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return 'Hello World!'

        with self.app_2.app_context():
            with current_app.test_request_context():
                response = self.autodoc.json()

        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('endpoints', data)
        self.assertEqual(data['endpoints'], [])
