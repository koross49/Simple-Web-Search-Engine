import secrets
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import jieba
import app.public_const

bootstrap = Bootstrap()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    bootstrap.init_app(app)
    csrf.init_app(app)
    CORS(app, supports_credentials=True)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config["SECRET_KEY"] = secrets.token_hex(16) 
    app.config["WTF_CSRF_SECRET_KEY"] = secrets.token_hex(16)

    from app.front import front as front_blueprint
    app.register_blueprint(front_blueprint)

    return app
