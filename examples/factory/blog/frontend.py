from json import dumps

from flask import Blueprint, redirect, request

from .doc import auto


frontend = Blueprint('frontend', __name__, url_prefix='/blog')

users = []
posts = []


class User(object):
    def __init__(self, username):
        self.username = username
        users.append(self)
        self.id = users.index(self)

    def __repr__(self):
        return dumps(self.__dict__)


class Post(object):
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        posts.append(self)
        self.id = posts.index(self)

    def __repr__(self):
        return dumps(self.__dict__)


u = User('acoomans')
Post('First post', 'This is the first awesome post', u)
Post('Second post', 'This is another even more awesome post', u)


@frontend.route('/')
@frontend.route('/posts')
@auto.doc(groups=['posts', 'public', 'private'])
def get_posts():
    """Return all posts."""
    return '%s' % posts


@frontend.route('/post/<int:id>')
@auto.doc(groups=['posts', 'public', 'private'])
def get_post(id):
    """Return the post for the given id."""
    return '%s' % posts[id]


@frontend.route('/post', methods=["POST"])
@auto.doc(groups=['posts', 'private'])
def post_post():
    """Create a new post.
    Form Data: title, content, authorid.
    """
    authorid = request.form.get('authorid', None)
    Post(request.form['title'],
         request.form['content'],
         users[authorid])
    return redirect("/posts")


@frontend.route('/users')
@auto.doc(groups=['users', 'public', 'private'])
def get_users():
    """Return all users."""
    return '%s' % users


@frontend.route('/user/<int:id>')
@auto.doc(groups=['users', 'public', 'private'])
def get_user(id):
    """Return the user for the given id."""
    return '%s' % users[id]


@frontend.route('/users', methods=['POST'])
@auto.doc(groups=['users', 'private'])
def post_user(id):
    """Create a new user.
    Form Data: username.
    """
    User(request.form['username'])
    redirect('/users')
