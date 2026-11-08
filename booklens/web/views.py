from flask import render_template

from booklens.web import web_bp


@web_bp.route("/")
def home():
    return render_template("home.html")
