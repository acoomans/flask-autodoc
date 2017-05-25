import json
import unittest

from flask import Flask
from flask.ext.autodoc import Autodoc


class TestAutodocWithFlask(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.autodoc = Autodoc(self.app)

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
