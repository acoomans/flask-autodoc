import os
import sys
import unittest

from examples.custom.blog import app as custom_app
from examples.simple.blog import app as simple_app

from tests.config import IS_WINDOWS

# To regenerate the baseline data files, change this to True.
REGENERATE_FILES = False


class TestApp(unittest.TestCase):
    maxDiff = None
    path = None
    filename = None
    app = None

    def setUp(self):
        if self.__class__ != TestApp:
            self.client = self.app.test_client()

    def get_request(self):
        r = self.client.get(self.path)
        self.assertEqual(r.status_code, 200)
        data = r.data.decode('utf-8')
        return data

    def sub_pwd(self, data):
        file_path = os.getcwd()
        return data.replace(file_path, "%PATH%")

    @unittest.skipIf(REGENERATE_FILES, "Regenerating the baseline files")
    @unittest.skipIf(IS_WINDOWS, "This test will not work with Windows style filepaths")
    def test_output(self):
        if self.__class__ == TestApp:
            self.skipTest('base test class')
        data = self.get_request()
        data = self.sub_pwd(data)
        with open(self.filename) as f:
            expected = f.read()
        self.assertEqual(data, expected)

    @unittest.skipIf(not REGENERATE_FILES, "This is only run to regenerate the baseline.")
    def test_regenerate(self):
        if self.__class__ == TestApp:
            self.skipTest('base test class')
        data = self.get_request()
        data = self.sub_pwd(data)
        with open(self.filename, "w") as f:
            f.write(data)
        self.assertTrue(False, "This test always fails, change REGENERATE_FILES back to False to proceed.")


class TestSimpleApp(TestApp):
    app = simple_app
    filename = "tests/files/simple.html"
    path = "/doc"


class TestSimpleAppJSONOutput(TestApp):
    app = simple_app
    filename = "tests/files/simple.json"
    path = "/doc/json"


class TestSimpleAppBuiltinJSONOutput(TestApp):
    app = simple_app
    filename = "tests/files/builtin.json"
    path = "/doc/builtin_json"


class TestSimpleAppPrivateGroup(TestApp):
    app = simple_app
    filename = "tests/files/simple_private.html"
    path = "/doc/private"


class TestFactoryApp(TestApp):
    filename = "tests/files/factory.html"
    path = "/doc/"

    @classmethod
    def setUpClass(cls):
        sys.path.append('examples/factory')
        from app import create_app as factory_create_app
        cls.app = factory_create_app()


class TestCustomApp(TestApp):
    app = custom_app
    filename = "tests/files/custom.html"
    path = "/doc/"


class TestCustomAppJSONOutput(TestApp):
    app = custom_app
    filename = "tests/files/custom.json"
    path = "/doc/json"


if __name__ == "__main__":
    unittest.main()
