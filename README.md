Flask-Autodoc
=============

Flask Autodoc is a Flask extension that automatically creates documentation for your endpoints based on the routes,
function arguments and docstring.

## Install

To install Flask-Autodoc:

    python setup.py install

## Usage

Start using Flask-Autodoc by importing it and initializing it:

    from flask import Flask
    from flask.ext.autodoc import Autodoc
    
    app = Flask(__name__)
    auto = Autodoc(app)

by default, Flask-Autodoc will only document the routes you explicitly tell him to with the _doc_ decorator,
like this:
  
    @app.route('/user/<int:id>')
    @auto.doc
    def show_user(id):
        """This returns a user with a given id."""
        return user_from_database(id)

to generate the documentation from an endpoint, use the _html()_ method:

    @app.route('/documentation')
    def documentation():
        return auto.html()

if you to access the documentation without it being rendered in html:

    @app.route('/documentation')
    def documentation():
        return auto.generate()

the documentation will then be returned as a list of rules, where each rule is a dictionary containing:

- methods: the set of allowed methods (ie ['GET', 'POST'])
- rule: relative url (ie '/user/<int:id>')
- endpoint: function name (ie 'show_user')
- doc: docstring of the function
- args: function arguments
- defaults: defaults values for the arguments

## Groups

You may want to group endpoints together, to have different documentation sets. With this you can for example, only
show some endpoints to third party developer and have full documentation for your own.

to assign an endpoint to a group, pass the name of the group as argument of the _doc_ decorator:

    @app.route('/user/<int:id>')
    @auto.doc("public")
    def show_user(id):

to assign an endpoint to multiple groups, pass a list of group names as the _groups_ argument to _doc_:

    @app.route('/user/<int:id>')
    @auto.doc(groups=["public","private"])
    def show_user(id):

to generate the documentation for a specific group, pass the name of the group to the _generate_ or _html_ methods:

    auto.generate("public")

or

    auto.html("public")
