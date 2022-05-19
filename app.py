from flask import Flask
from flask.json import JSONEncoder
from database import sesh, init_db
from datetime import datetime as dt




class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, dt):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config.from_pyfile("config.py", silent=True)
    with app.app_context():
        # Import app routes
        import routes
        # Initialize Global db
        import models
        init_db()

        return app


if __name__ == "__main__":
    try:
        app = create_app()
        print(app.config)
        app.run(host="127.0.0.1", port=8473, debug=True)
    except Exception as e:
        print("Application Error: ", e, "\n\n", e.args, "\n")
