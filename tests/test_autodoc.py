import inspect
import os.path
import unittest
import sys
import os

from flask import Flask
from flask_autodoc import Autodoc


class TestAutodoc(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.debug = True
        self.autodoc = Autodoc(self.app)

    @staticmethod
    def thisFile():
        """Returns the basename of __file__ without a trailing 'c'"""
        filename = os.path.basename(__file__)
        if filename.endswith('.pyc'):
            filename = filename[:-1]
        return filename

    def testGet(self):
        @self.app.route('/')
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return 'Hello World!'

        with self.app.app_context():
            doc = self.autodoc.generate()
        self.assertTrue(len(doc) == 1)
        d = doc[0]
        self.assertIn('GET', d['methods'])
        self.assertNotIn('POST', d['methods'])
        self.assertEqual(d['rule'], '/')
        self.assertEqual(d['endpoint'], 'index')
        self.assertEqual(d['docstring'], 'Returns a hello world message')
        self.assertIsInstance(d['location']['line'], int)
        self.assertIn(self.thisFile(), d['location']['filename'])
        self.assertFalse(d['defaults'])

    def testPost(self):
        @self.app.route('/', methods=['POST'])
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return 'Hello World!'

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 1)
            d = doc[0]
            self.assertIn('POST', d['methods'])
            self.assertNotIn('GET', d['methods'])
            self.assertEqual(d['rule'], '/')
            self.assertEqual(d['endpoint'], 'index')
            self.assertEqual(d['docstring'], 'Returns a hello world message')
            self.assertIsInstance(d['location']['line'], int)
            self.assertIn(self.thisFile(), d['location']['filename'])
            self.assertFalse(d['defaults'])

    def testParams(self):
        @self.app.route('/p1/p2', defaults={'param1': 'a', 'param2': 'b'})
        @self.app.route('/p1/<string:param1>/p2/<int:param2>')
        @self.autodoc.doc()
        def ab(param1, param2):
            return 'param1=%s param2=%s' % (param1, param2)

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 2)

            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertTrue('/p1/p2' in rules)
            self.assertTrue('/p1/<string:param1>/p2/<int:param2>' in rules)

            for d in doc:
                self.assertEqual(d['endpoint'], 'ab')
                self.assertIsNone(d['docstring'])

                if '/p1/p2' in d['rule']:
                    self.assertDictEqual(d['defaults'],
                                         {'param2': 'b', 'param1': 'a'})
                elif '/p1/<string:param1>/p2/<int:param2>' in d['rule']:
                    self.assertFalse(d['defaults'])

    def testGroup(self):
        @self.app.route('/pri')
        @self.autodoc.doc('private')
        def pri():
            return 'This is a private endpoint'

        @self.app.route('/pub')
        @self.autodoc.doc('public')
        def pub():
            return 'This is a public endpoint'

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 2)

            doc = self.autodoc.generate('all')
            self.assertTrue(len(doc) == 2)

            doc = self.autodoc.generate('private')
            self.assertTrue(len(doc) == 1)
            self.assertIn('/pri', doc[0]['rule'])

            doc = self.autodoc.generate('public')
            self.assertTrue(len(doc) == 1)
            self.assertIn('/pub', doc[0]['rule'])

    def testGroups(self):
        @self.app.route('/a')
        @self.autodoc.doc()
        def a():
            return 'Hello world, a!'

        @self.app.route('/b')
        @self.autodoc.doc(groups=['group1', 'group2'])
        def b():
            return 'Hello world, b!'

        @self.app.route('/c')
        @self.autodoc.doc('group2')
        def c():
            return 'Hello world, c!'

        with self.app.app_context():
            doc = self.autodoc.generate()
            self.assertTrue(len(doc) == 3)

            doc = self.autodoc.generate('all')
            self.assertTrue(len(doc) == 3)

            doc = self.autodoc.generate('group1')
            self.assertTrue(len(doc) == 1)
            self.assertIn('/b', doc[0]['rule'])

            doc = self.autodoc.generate('group2')
            self.assertTrue(len(doc) == 2)
            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertIn('/b', rules)
            self.assertIn('/c', rules)

            doc = self.autodoc.generate(groups=['group2'])
            self.assertTrue(len(doc) == 2)
            rules = [doc[i]['rule'] for i in range(len(doc))]
            self.assertIn('/b', rules)
            self.assertIn('/c', rules)

    def testCustomParams(self):
        @self.app.route('/needsargs', methods=['GET'])
        @self.autodoc.doc('needs_getargs', getargs={
            'a': 'A Value',
            'b': 'B Value'  
            })
        def getit():
            return 'I need specific GET parameters.'

        @self.app.route('/noargs')
        @self.autodoc.doc(groups=['needs_json', 'noargs'],
            expected_type='application/json')
        def needjson():
            return 'I do not need any parameters, but am picky about types.'

        with self.app.app_context():
            doc = self.autodoc.generate('needs_getargs')
            self.assertTrue(len(doc) == 1)
            self.assertIn('getargs', doc[0])
            self.assertEqual('B Value', doc[0]['getargs']['b'])

            doc = self.autodoc.generate('noargs')
            self.assertTrue(len(doc) == 1)
            self.assertNotIn('getargs', doc[0])

            doc = self.autodoc.generate('needs_json')
            self.assertTrue(len(doc) == 1)
            self.assertIn('expected_type', doc[0])
            self.assertEqual('application/json', doc[0]['expected_type'])

    def testOverrideParams(self):
        @self.app.route('/added')
        @self.autodoc.doc('add', args=['option'])
        def original():
            return 'I make my own options.'

        @self.app.route('/modified', defaults={'option1': 1})
        @self.app.route('/modified/<int:option1>')
        @self.autodoc.doc('modify', args=['option2'], defaults=[2])
        def override_allowed(option1):
            return 'I modify my own options.'

        @self.app.route('/prohibited')
        @self.autodoc.doc('fail', rule='/not/supposed/to/be/here')
        def override_prohibited():
            return 'I make my own rules.'

        with self.app.app_context():
            doc = self.autodoc.generate('add')
            self.assertTrue(len(doc) == 1)
            self.assertIn('option', doc[0]['args'])

            doc = self.autodoc.generate('modify')
            args = [doc[i]['args'] for i in range(len(doc))]
            defaults = [doc[i]['defaults'] for i in range(len(doc))]
            self.assertNotIn(['option1'], args)
            self.assertNotIn([1], defaults)
            self.assertIn(['option2'], args)
            self.assertIn([2], defaults)

            doc = self.autodoc.generate('fail')
            self.assertTrue(len(doc) == 1)
            self.assertNotEqual('/not/supposed/to/be/here', doc[0]['rule'])
            self.assertEqual('/prohibited', doc[0]['rule'])

    def testHTML(self):
        @self.app.route('/')
        @self.autodoc.doc()
        def index():
            """Returns a hello world message"""
            return 'Hello World!'

        with self.app.app_context():
            doc = self.autodoc.html()
            self.assertIn('/', doc)
            self.assertIn('Returns a hello world message', doc)

    def testHTMLWithArgs(self):
        @self.app.route('/p1/p2', defaults={'param1': 'a', 'param2': 'b'})
        @self.app.route('/p1/<string:param1>/p2/<int:param2>')
        @self.autodoc.doc()
        def ab(param1, param2):
            """Returns arguments

            This endpoint returns the value of the 2 parameters:
            - param1
            - param2
            """
            return 'param1=%s param2=%s' % (param1, param2)

        with self.app.app_context():
            doc = self.autodoc.html(title='hello')
            self.assertIn('/p1/p2', doc)
            if sys.version < '3':
                self.assertRegexpMatches(
                    doc,
                    '\/p1\/.*string:param1.*\/p2\/.*int:param2.*'
                )
            else:
                self.assertRegex(
                    doc,
                    '\/p1\/.*string:param1.*\/p2\/.*int:param2.*'
                )
            self.assertIn('Returns arguments', doc)

    def testLocation(self):
        line_no = inspect.stack()[0][2] + 2 # the doc() line
        @self.app.route('/location')
        @self.autodoc.doc()
        def location():
            return 'location'

        with self.app.app_context():
            doc = self.autodoc.generate()
            d = doc[0]
            self.assertIsInstance(d['location']['line'], int)
            self.assertEqual(d['location']['line'], line_no)
            self.assertIn(self.thisFile(), d['location']['filename'])

    def testNoLocation(self):
        @self.app.route('/location')
        @self.autodoc.doc(set_location=False)
        def location():
            return 'location'

        with self.app.app_context():
            doc = self.autodoc.generate()
            d = doc[0]
            self.assertIsNone(d['location'])

    def testRedecorate(self):
        @self.app.route('/redecorate')
        # add to "all" and "group1"
        @self.autodoc.doc('group1')
        def redecorate():
            return 'redecorate'

        # add to "group2"
        self.app.view_functions['redecorate'] = self.autodoc.doc('group2')(redecorate)

        with self.app.app_context():
            self.assertTrue(1 == len(self.autodoc.generate('all')))
            self.assertTrue(1 == len(self.autodoc.generate('group1')))
            self.assertTrue(1 == len(self.autodoc.generate('group2')))
            self.assertFalse(1 == len(self.autodoc.generate('group3')))

