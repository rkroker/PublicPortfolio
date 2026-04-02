"""
Author: Ryan Kroker (ryan.kroker@gmail.com)
Version: 1.0
Created: 3-27-2026
Last Updated: 4-2-2026
Purpose: Handles Flask application setup, shared filters, and startup configuration for the activity emailer.
"""

import os
from datetime import timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from flask import Flask
from config import Config
from models import db
from routes import main

load_dotenv()


def format_datetime_local(value):
    if not value:
        return ""

    utc_value = value.replace(tzinfo=timezone.utc)
    local_value = utc_value.astimezone(ZoneInfo("America/New_York"))
    return local_value.strftime("%Y-%m-%d %I:%M %p")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    app.register_blueprint(main)
    app.jinja_env.filters["datetime_local"] = format_datetime_local

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)