from flask import Flask


def create_app(config_filename=None):
    app = Flask(__name__)
    app.debug = True

    from blog import auto
    auto.init_app(app)

    if config_filename:
        app.config.from_pyfile(config_filename)

    from blog import admin, frontend, doc
    app.register_blueprint(admin)
    app.register_blueprint(frontend)
    app.register_blueprint(doc)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
