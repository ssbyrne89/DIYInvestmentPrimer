# web_app/routes/company_routes.py

from flask import Blueprint, jsonify, request, render_template #, flash, redirect

company_routes = Blueprint("company_routes", __name__)

@company_routes.route("/companies.json")
def list_companies():
    companies = [
        {"id": 1, "title": "Company 1"},
        {"id": 2, "title": "Company 2"},
        {"id": 3, "title": "Company 3"},
    ]
    return jsonify(companies)

@company_routes.route("/companies")
def list_companies_for_humans():
    companies = [
        {"id": 1, "title": "Company 1"},
        {"id": 2, "title": "Company 2"},
        {"id": 3, "title": "Company 3"},
    ]
    return render_template("dividend_companies.html", message="Here's some companies", companies=companies)