import unittest
from flask import Flask
from flask.ext.autodoc import Autodoc

class TestAutodoc(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.debug = True
        self.autodoc = Autodoc(self.app)

    def testGet(self):
        @self.app.route("/")
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return "Hello World!"

        with self.app.app_context():
            doc = self.autodoc.generate()
        self.assertTrue(len(doc) == 1)
        d = doc[0]
        self.assertIn('GET', d['methods'])
        self.assertNotIn('POST', d['methods'])
        self.assertEqual(d['rule'], '/')
        self.assertEqual(d['endpoint'], 'index')
        self.assertEqual(d['docstring'], "Returns a hello world message")
        self.assertFalse(d['defaults'])

    def testPost(self):
        @self.app.route("/", methods=['POST'])
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return "Hello World!"

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 1)
            d = doc[0]
            self.assertIn('POST', d['methods'])
            self.assertNotIn('GET', d['methods'])
            self.assertEqual(d['rule'], '/')
            self.assertEqual(d['endpoint'], 'index')
            self.assertEqual(d['docstring'], "Returns a hello world message")
            self.assertFalse(d['defaults'])

    def testParams(self):
        @self.app.route("/p1/p2", defaults={'param1': 'a', 'param2': 'b'})
        @self.app.route("/p1/<string:param1>/p2/<int:param2>")
        @self.autodoc.doc()
        def ab(param1, param2):
            return "param1=%s param2=%2" % (param1, param2)

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 2)

            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertTrue("/p1/p2" in rules)
            self.assertTrue("/p1/<string:param1>/p2/<int:param2>" in rules)

            for d in doc:
                self.assertEqual(d['endpoint'], 'ab')
                self.assertIsNone(d['docstring'])

                if "/p1/p2" in d['rule']:
                    self.assertDictEqual(d['defaults'], {'param2': 'b', 'param1': 'a'})
                elif "/p1/<string:param1>/p2/<int:param2>" in d['rule']:
                    self.assertFalse(d['defaults'])

    def testGroup(self):
        @self.app.route("/pri")
        @self.autodoc.doc("private")
        def pri():
            return "This is a private endpoint"

        @self.app.route("/pub")
        @self.autodoc.doc("public")
        def pub():
            return "This is a public endpoint"

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 2)

            doc = self.autodoc.generate("all")
            self.assertTrue(len(doc) == 2)

            doc = self.autodoc.generate("private")
            self.assertTrue(len(doc) == 1)
            self.assertIn("/pri", doc[0]['rule'])

            doc = self.autodoc.generate("public")
            self.assertTrue(len(doc) == 1)
            self.assertIn("/pub", doc[0]['rule'])

    def testGroups(self):

        @self.app.route("/a")
        @self.autodoc.doc()
        def a():
            return "Hello world, a!"

        @self.app.route("/b")
        @self.autodoc.doc(groups=["group1", "group2"])
        def b():
            return "Hello world, b!"

        @self.app.route("/c")
        @self.autodoc.doc("group2")
        def c():
            return "Hello world, c!"

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 3)

            doc = self.autodoc.generate("all")
            self.assertTrue(len(doc) == 3)

            doc = self.autodoc.generate("group1")
            self.assertTrue(len(doc) == 1)
            self.assertIn("/b", doc[0]['rule'])

            doc = self.autodoc.generate("group2")
            self.assertTrue(len(doc) == 2)
            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertIn("/b", rules)
            self.assertIn("/c", rules)

            doc = self.autodoc.generate(groups=["group2"])
            self.assertTrue(len(doc) == 2)
            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertIn("/b", rules)
            self.assertIn("/c", rules)

    def testHTML(self):
        @self.app.route("/")
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return "Hello World!"

        with self.app.app_context():
            doc = self.autodoc.html()
            self.assertIn("/", doc)
            self.assertIn("Returns a hello world message", doc)

    def testHTMLWithArgs(self):
        @self.app.route("/p1/p2", defaults={'param1': 'a', 'param2': 'b'})
        @self.app.route("/p1/<string:param1>/p2/<int:param2>")
        @self.autodoc.doc()
        def ab(param1, param2):
            """Returns arguments

            This endpoint returns the value of the 2 parameters:
            - param1
            - param2
            """
            return "param1=%s param2=%2" % (param1, param2)

        with self.app.app_context():
            doc = self.autodoc.html(title="hello")
            self.assertIn("/p1/p2", doc)
            self.assertRegexpMatches(doc, "\/p1\/.*string:param1.*\/p2\/.*int:param2.*")
            self.assertIn("Returns arguments", doc)