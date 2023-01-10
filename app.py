from flask import Flask, logging
from flask.json import JSONEncoder

from datetime import datetime as dt
import logging
import subprocess
import argparse
from pathlib import Path


def validPath(path):
    p = Path(path)
    if not p.is_dir():
        raise argparse.ArgumentTypeError(
            f"{path} is invalid: not a directory")
    else:
        return p.resolve()


def makeParser():
    parser = argparse.ArgumentParser()
    parser.add_help = "Flask app options"
    parser.add_argument("-dt", "--drop", help="Drop a table",
                        action="store", required=False,  type=str, dest="dropTable")
    # parser.add_argument("-r", "--replica", help="Path to replica folder", default="./replica",
    #                     action="store", required=True, type=mkPath)
    # parser.add_argument("-l", "--logPath", action="store", help="Directory for logfile. Default is Path.cwd()",
    #                     type=validPath, default=Path.cwd())
    parser.add_argument("-dbg", "--debug", help="Enable debugger",
                        action="store", type=bool, default=True)
    return parser


def run_before_flask(*args):
    if args:
        pass
    s = subprocess.run(["sass", "static/_styles/base.scss",
                       "static/style.css"], check=True)
    if s.stdout:
        logging.info("SASS compiled styles")
    return


def makeLogger(logPath):
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s #[%(lineno)s] [%(levelname)-4.7s]  %(message)s %(args)s",
        handlers=[logging.FileHandler(
            f"{logPath}/log.log"), logging.StreamHandler()],
        encoding="utf-8"
    )
    return logging.getLogger()


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


def create_app(args):
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config.from_pyfile("config.py", silent=False)
    app.secret_key = app.config["SECRET_KEY"]
    with app.app_context():
        # Import app routes
        try:
            from database import db
            # Initialize Global db
            import models
            import models_dev
            db.configure()
            db.init_db()
        except Exception as e:
            log.error(e.args)
            raise
        import routes
        return app


if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    log = makeLogger("static/")
    try:
        if args.dropTable:
            from controller import dropTable
            dropTable(table=args.dropTable)
        run_before_flask(args)
    except Exception as e:
        log.error(e.args)
    app = create_app(args)
    with app.app_context() as ctx:
        log.info(f"Running {__name__}")
        app.run(host="127.0.0.1", port=8473, debug=True)
