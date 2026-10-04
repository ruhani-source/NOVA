from flask import Flask
from flask_cors import CORS

from backend.routes import api

from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.register_blueprint(api)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)