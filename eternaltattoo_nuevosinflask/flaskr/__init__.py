import os
from flask import Flask

def create_app(test_config=None):
    # Creation and configuration of the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        UPLOAD_DIR=os.path.join(app.instance_path, "uploads"),
        POSTS_PER_PAGE=5
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config["UPLOAD_DIR"])
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    from . import search
    app.register_blueprint(search.bp)

    from . import images
    app.register_blueprint(images.bp)

    from . import comments
    app.register_blueprint(comments.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    from . import likes
    app.register_blueprint(likes.bp)
    
    from . import followers
    app.register_blueprint(followers.bp)

    return app

