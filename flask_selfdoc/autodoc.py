import json
from operator import attrgetter, itemgetter
import os
import re
from collections import defaultdict
import sys
import inspect
from typing import Optional, Tuple

from flask import current_app, render_template, render_template_string, jsonify
from jinja2.exceptions import TemplateAssertionError

try:
    # Jinja2 < 3.1 (Flask <= 2.0 and python 3.6)
    # https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.evalcontextfilter
    from jinja2 import evalcontextfilter as pass_eval_context
except ImportError:
    # Jinja2 < 3.1 (Flask >= 2.0 and python <= 3.7)
    from jinja2 import pass_eval_context

try:
    # Jinja2 < 3.1 (Flask <= 2.0 and python 3.6)
    from jinja2 import Markup
except ImportError:
    # Jinja2 < 3.1 (Flask >= 2.0 and python <= 3.7)
    from jinja2.utils import markupsafe
    Markup = markupsafe.Markup

try:
    from flask.globals import _cv_app
except ImportError:
    _cv_app = None
    try:
        from flask import _app_ctx_stack as stack
    except ImportError:
        from flask import _request_ctx_stack as stack


if sys.version < '3':
    get_function_code = attrgetter('func_code')
else:
    get_function_code = attrgetter('__code__')


def custom_jsonify(*args,
                   indent: Optional[int] = None,
                   separators: Optional[Tuple] = (',', ':'),
                   **kwargs):
    response = jsonify(*args, **kwargs)
    json_data = json.loads(response.data.decode('utf-8'))
    json_string = json.dumps(json_data,
                             indent=indent,
                             separators=separators)
    response.data = json_string.encode('utf-8')
    return response


def get_decorator_frame_info(frame) -> dict:
    """
    The way that the line number of a decorator is detected changed across
    python versions:
    - python <= 3.8:
      stack()[1].lineno points to the line above the decorated function
      => points to the closest decorator, not necessarily the one that did the
         call to stack()
    - python 3.9 and 3.10:
      stack()[1].lineno points to the line of the decorated function
    - python 3.11:
      stack()[1].lineno points to the exact line of the decorator that did the
      call to stack()

    Example:

    1   |def call_stack_and_get_lineno():
    2   |
    3   |    def decorator(func):
    4   |        calling_frame = stack()[1]
    5   |        print(calling_frame.lineno)
    6   |        return func
    7   |
    8   |    return decorator
    9   |
    10  |
    11  |@decorator1
    12  |@call_stack_and_get_lineno
    13  |@decorator2
    14  |def func():
    15  |    pass

    - python <= 3.8: will print line 13
    - python 3.9 and 3.10: will print line 14 (desired behaviour)
    - python 3.11: will print line 12

    We adjust the found line number with some offset (by reading the python
    source file) if required.
    """
    line_number = frame.lineno
    try:
        with open(frame.filename, 'r') as python_file:
            python_lines = python_file.readlines()
        # current line + next ones
        context_lines = python_lines[line_number - 1:]
    except (OSError, FileNotFoundError):
        print("You're probably using flask_selfdoc with compiled python code "
              "- prefer uncompiled source files to extract correct filenames "
              "and line numbers.")
        # not 100% correct solution, won't work for multiline decorator
        # or if there are decorators between @autodoc.doc() and the endpoint
        # function
        context_lines = frame.code_context

    # if the detected line number doesn't point to a function definition,
    # we iterate until we find one.
    for line in context_lines:
        if not line.strip().startswith('def '):
            line_number += 1
        else:
            break

    return {
        'filename': frame.filename,
        'line': line_number,
    }


class Autodoc(object):

    def __init__(self, app=None):
        self.app = app
        self.func_groups = defaultdict(set)
        self.func_props = defaultdict()
        self.immutable_props = ['rule', 'endpoint']
        self.default_props = [
            'methods', 'docstring',
            'args', 'defaults', 'location'] + self.immutable_props
        self.func_locations = defaultdict(dict)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)
        self.add_custom_template_filters(app)

    def teardown(self, exception):
        if _cv_app is not None:
            ctx = _cv_app.get(None)  # noqa: F841
        else:
            ctx = stack.top  # noqa: F841

    def add_custom_template_filters(self, app):
        """Add custom filters to jinja2 templating engine"""
        self.add_custom_nl2br_filters(app)

    def add_custom_nl2br_filters(self, app):
        """Add a custom filter nl2br to jinja2
         Replaces all newline to <BR>
        """
        _paragraph_re = re.compile(r'(?:\r\n|\r|\n){3,}')

        @app.template_filter()
        @pass_eval_context
        def nl2br(eval_ctx, value):
            result = '\n\n'.join('%s' % p.replace('\n', Markup('<br>\n'))
                                 for p in _paragraph_re.split(value))
            return result

    def doc(self, groups=None, set_location=True, **properties):
        """Add flask route to autodoc for automatic documentation

        Any route decorated with this method will be added to the list of
        routes to be documented by the generate() or html() methods.

        By default, the route is added to the 'all' group.
        By specifying group or groups argument, the route can be added to one
        or multiple other groups as well, besides the 'all' group.

        If set_location is True, the location of the function will be stored.
        NOTE: this assumes that the decorator is placed just before the
        function (in the normal way).

        Custom parameters may also be passed in beyond groups, if they are
        named something not already in the dict descibed in the docstring for
        the generate() function, they will be added to the route's properties,
        which can be accessed from the template.

        If a parameter is passed in with a name that is already in the dict, but
        not of a reserved name, the passed parameter overrides that dict value.
        """
        def decorator(f):
            # Get previous group list (if any)
            if f in self.func_groups:
                groupset = self.func_groups[f]
            else:
                groupset = set()

            # Set group[s]
            if type(groups) is list:
                groupset.update(groups)
            elif type(groups) is str:
                groupset.add(groups)
            groupset.add('all')
            self.func_groups[f] = groupset
            self.func_props[f] = properties

            # Set location
            if set_location:
                caller_frame = inspect.stack()[1]
                self.func_locations[f] = get_decorator_frame_info(caller_frame)

            return f
        return decorator

    def generate(self, groups='all', sort=None):
        """Return a list of dict describing the routes specified by the
        doc() method

        Each dict contains:
         - methods: the set of allowed methods (ie ['GET', 'POST'])
         - rule: relative url (ie '/user/<int:id>')
         - endpoint: function name (ie 'show_user')
         - docstring: docstring of the function
         - args: function arguments
         - defaults: defaults values for the arguments

        By specifying the group or groups arguments, only routes belonging to
        those groups will be returned.

        Routes are sorted alphabetically based on the rule.
        """
        groups_to_generate = list()
        if type(groups) is list:
            groups_to_generate = groups
        elif type(groups) is str:
            groups_to_generate.append(groups)

        links = []
        for rule in current_app.url_map.iter_rules():

            if rule.endpoint == 'static':
                continue

            func = current_app.view_functions[rule.endpoint]
            arguments = sorted(list(rule.arguments)) if rule.arguments else ['None']
            func_groups = self.func_groups[func]
            func_props = self.func_props[func] if func in self.func_props \
                else {}
            location = self.func_locations.get(func, None)

            if func_groups.intersection(groups_to_generate):
                props = dict(
                    methods=sorted(list(rule.methods)),
                    rule="%s" % rule,
                    endpoint=rule.endpoint,
                    docstring=func.__doc__.strip(' ') if func.__doc__ else None,
                    args=arguments,
                    defaults=rule.defaults or dict(),
                    location=location,
                )
                for p in func_props:
                    if p not in self.immutable_props:
                        props[p] = func_props[p]
                links.append(props)
        if sort == "lexical":
            sort = sort_lexically
        if sort:
            return sort(links)
        else:
            return sorted(links, key=itemgetter('rule'))

    def html(self, groups='all', template=None, **context):
        """Return an html string of the routes specified by the doc() method

        A template can be specified. A list of routes is available under the
        'autodoc' value (refer to the documentation for the generate() for a
        description of available values). If no template is specified, a
        default template is used.

        By specifying the group or groups arguments, only routes belonging to
        those groups will be returned.
        """
        context['autodoc'] = context['autodoc'] if 'autodoc' in context \
            else self.generate(groups=groups)
        context['defaults'] = context['defaults'] if 'defaults' in context \
            else self.default_props
        if template:
            return render_template(template, **context)
        else:
            filename = os.path.join(
                os.path.dirname(__file__),
                'templates',
                'autodoc_default.html'
            )
            with open(filename) as file:
                content = file.read()
                with current_app.app_context():
                    try:
                        return render_template_string(content, **context)
                    except TemplateAssertionError:
                        raise RuntimeError(
                            "Autodoc was not initialized with the Flask app.")

    def json(self,
             groups='all',
             indent: Optional[int] = None,
             separators: Optional[Tuple] = (',', ':')):
        """Return a json object with documentation for all the routes specified
        by the doc() method.

        By specifiying the groups argument, only routes belonging to those groups
        will be returned.
        """
        autodoc = self.generate(groups=groups)

        def endpoint_info(doc):
            args = sorted(doc['args'])
            if args == ['None']:
                args = []
            return {
                "args": [(arg, doc['defaults'].get(arg, None)) for arg in args],
                "docstring": doc['docstring'],
                "methods": doc['methods'],
                "rule": doc['rule']
            }
        data = {
            'endpoints':
                [endpoint_info(doc) for doc in autodoc]
        }
        return custom_jsonify(data, indent=indent, separators=separators)


def sort_lexically(links):
    def parts(endpoint):
        rule = endpoint['rule']
        return rule.split("/")

    return sorted(links, key=parts)


Selfdoc = Autodoc
