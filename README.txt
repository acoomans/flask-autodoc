Flask-Selfdoc
=============

Flask-Selfdoc is a Flask extension that automatically creates documentation for your endpoints based on the routes, function arguments and docstrings. It was forked from Flask-Autodoc, written by Arnaud Coomans, and is completely compatible as a replacement for that extension.

Flask-Selfdoc is compatible with Python versions 2 and 3; and it depends only on Flask. It is tested with all versions of Flask from 0.11 up to the latest release and the latest Flask release will continue to be supported.

If your codebase uses Flask-Autodoc, you can swap it for Flask-Selfdoc by simply changing the name of the module in your import:

    from flask_selfdoc import Autodoc
    
instead of 

    from flask_autodoc import Autodoc
    
No other changes are necessary. Flask-Selfdoc 1.0 has exactly the same functionality as Flask-Autodoc 0.1.2, the most recent release at the time of the fork. The projects will remain like-for-like compatible for the foreseeable future.

The full documentation is at https://github.com/jwg4/flask-selfdoc/blob/master/README.md