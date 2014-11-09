from flask import Flask
from flask.ext.autodoc import Autodoc


app = Flask(__name__)
app.debug = True
auto = Autodoc(app)


@app.route('/', methods=['GET'])
@auto.doc()
def rst():
    """reStructuredText example.

    If docutils is installed, this docstring in reStructuredText should render
    properly.

    This is *italics*, **bold**, ``code``.

    A bullet list:

    * one item
    * a second item

    A numbered list:

    1. one item
    2. a second item

    Sample code:

        echo "hello"

    A `link <http://example.com>`_

    :param param1: a parameter
    :param param2: a parameter
    :return: a return value
    :raise: an exception

    An image:

    .. image:: https://avatars0.githubusercontent.com/u/733352?v=3&s=100

    """
    return 'rst'


@app.route('/doc')
@app.route('/doc/public')
@app.route('/doc/private')
def public_doc():
    return auto.html(
        template='rst.html',
        title='reStructuredText Example',
    )

if __name__ == '__main__':
    app.run()
