import sys
import unittest

from examples.custom.blog import app as custom_app
from examples.simple.blog import app as simple_app


class TestApp(object):
    maxDiff = None

    def setUp(self):
        self.client = self.app.test_client()

    def test_output(self):
        r = self.client.get(self.path)
        self.assertEqual(r.status_code, 200)
        data = r.data.decode('utf-8')
        with open(self.filename) as f:
            expected = f.read()

        self.assertEqual(data, expected)


class TestSimpleApp(TestApp, unittest.TestCase):
    app = simple_app
    filename = "tests/files/simple.html"
    path = "/doc"


class TestSimpleAppJSONOutput(TestApp, unittest.TestCase):
    app = simple_app
    filename = "tests/files/simple.json"
    path = "/doc/json"


class TestSimpleAppPrivateGroup(TestApp, unittest.TestCase):
    app = simple_app
    filename = "tests/files/simple_private.html"
    path = "/doc/private"


class TestFactoryApp(TestApp, unittest.TestCase):
    filename = "tests/files/factory.html"
    path = "/doc/"

    @classmethod
    def setUpClass(cls):
        sys.path.append('examples/factory')
        from app import create_app as factory_create_app
        cls.app = factory_create_app()


class TestCustomApp(TestApp, unittest.TestCase):
    app = custom_app
    filename = "tests/files/custom.html"
    path = "/doc/"


if __name__ == "__main__":
    unittest.main()
