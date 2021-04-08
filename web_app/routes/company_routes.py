# web_app/routes/company_routes.py
import pandas as pd
from flask import Blueprint, jsonify, request, render_template #, flash, redirect

from web_app.models import *

company_routes = Blueprint("company_routes", __name__)



@company_routes.route("/companies")
def list_companies_for_humans():
    return render_template("AllS&P500.html", message="Here's all the companies on the S&P 500",
                            companies=get_AllCompanies())

def get_AllCompanies():
    all = Company_Info.query.all()
    names = [record.Company_Name for record in all]
    return names


def createCompanyInfoTable():  # ran once
    SandP500 = pd.read_csv('../DIYInvestmentPrimer/SandP_500_companies.csv')

    for x in range(0, len(SandP500)):
        db.create_all()
        company_entry = Company_Info.query.get
        (Company_Info(Company_Name=SandP500['Security'][x],
                                     Company_Ticker=SandP500['Symbol'][x],
                                     Sector=SandP500['GICS Sector'][x],
                                     SubIndustry=SandP500['GICS Sub-Industry'][x],
                                     HQ_Location=SandP500['Headquarters Location'][x],
                                     Date_first_added_to_SP500=SandP500['Date first added'][x],
                                     Founded=SandP500['Founded'][x]))

        db.session.add(company_entry)
        db.session.commit()

    