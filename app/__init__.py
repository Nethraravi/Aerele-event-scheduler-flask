from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from . import models

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    
    from .routes import register_routes
    register_routes(app)


    return app
