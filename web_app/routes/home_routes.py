# web_app/routes/home_routes.py

from flask import Blueprint, render_template



home_routes = Blueprint("home_routes", __name__)


@home_routes.route("/")
def index():
    return render_template("index.html")

@home_routes.route("/about")
def about():
    return render_template("about.html")

@home_routes.route("/wtmm")
def wtmm():
    return render_template("wtmm.html")

@home_routes.route("/real_estate_resources")
def REresources():
    return render_template("REresources.html")

@home_routes.route("/personal_finance_and_savings_resources")
def PFSresources():
    return render_template("PFSresources.html")