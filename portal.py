#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import json
import logging
import requests

from flask import Flask, Blueprint, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

import settings

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger("cuckoo.portal")

db = SQLAlchemy(session_options=dict(autoflush=True))
blueprint = Blueprint("index", __name__)

def emit_options(options):
    return ",".join("%s=%s" % (k, v) for k, v in options.items())

@blueprint.route("/")
def index():
    return render_template("index.html",
                           machines=["xp1", "xp2"],
                           routes=["none", "dirty", "vpn"])

def submit_file(f, data):
    files = {
        "file": (f.filename, f),
    }

    try:
        url = "http://%s:8090/tasks/create/file" % settings.CUCKOO_API
        r = requests.post(url, data=data, files=files)
        return r.json()["task_id"]
    except:
        log.exception("Error submitting file")

def submit_url(url, data):
    data["url"] = url

    try:
        url = "http://%s:8090/tasks/create/url" % settings.CUCKOO_API
        r = requests.post(url, data=data)
        return r.json()["task_id"]
    except:
        log.exception("Error submitting URL")

@blueprint.route("/", methods=["POST"])
def submit():
    files = request.files.getlist("file")
    urls = request.form.get("url", "")
    timeout = request.form.get("timeout")
    priority = request.form.get("priority")
    machine = request.form.get("machine")
    route = request.form.get("route")
    email = request.form.get("email")
    reports = request.form.getlist("report")

    tasks, errors = [], []

    if not timeout.isdigit():
        errors.append("Timeout is not a number, please specify the timeout in minutes.")
    elif int(timeout) < 1 or int(timeout) > 30:
        errors.append("Timeout must be between one and 30 minutes.")

    if not priority.isdigit():
        errors.append("Invalid priority given.")
    else:
        priority = int(priority)

    if not email:
        errors.append("Please specify an email address so to retrieve the analysis reports.")

    if "plain" not in reports and "html" not in reports and "pdf" not in reports:
        errors.append("You must select at least one reporting format.")

    if errors:
        return render_template("index.html", **locals())

    # TODO Check the route.

    options = {
        "procmemdump": "1",
        "route": route,
        "json.calls": "0",
    }

    custom = {
        "email": email,
        "reports": reports,
    }

    data = {
        "timeout": timeout * 60,
        "priority": priority,
        "machine": machine,
        "options": emit_options(options),
        "custom": json.dumps(custom),
    }

    for f in files:
        if not f.filename:
            continue

        task_id = submit_file(f, data)
        if task_id:
            tasks.append((task_id, f.filename))
        else:
            errors.append("Error submitting file: %s" % f.filename)

    for url in urls.split("\n"):
        url = url.strip()
        if not url:
            continue

        task_id = submit_url(url, data)
        if task_id:
            tasks.append((task_id, url))
        else:
            errors.append("Error submitting URL: %s" % url)

    if not tasks:
        if errors:
            errors.append(
                "It would appear our backend is down, please contact us to "
                "report this issue at your earliest convenience."
            )
        else:
            errors.append("At least one file or URL should be specified")

        return render_template("index.html", **locals())

    return render_template("submitted.html", **locals())

def create_app():
    app = Flask("Portal")
    app.config.from_object(settings)

    db.init_app(app)
    db.create_all(app=app)
    return app

application = create_app()
application.register_blueprint(blueprint)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", default="127.0.0.1", help="Host to listen on.")
    parser.add_argument("port", nargs="?", type=int, default=9004, help="Port to listen on.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    application.run(host=args.host, port=args.port, debug=True)
