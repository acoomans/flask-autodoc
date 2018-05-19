"""
Flask-Selfdoc
-------------

Flask selfdoc automatically creates an online documentation for your flask app.
"""
from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='Flask-Selfdoc',
    version='1.0rc1',
    url='http://github.com/jwg4/flask-selfdoc',
    license='MIT',
    author='Arnaud Coomans',
    maintainer='Jack Grahl',
    maintainer_email='jack.grahl@gmail.com',
    description='Documentation generator for flask',
    long_description=readme(),
    # py_modules=['flask_autodoc'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['flask_selfdoc'],
    package_data={'flask_selfdoc': ['templates/autodoc_default.html']},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='tests',
)
