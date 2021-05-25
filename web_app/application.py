# web_app/__init__.py

from flask import Flask, Blueprint, jsonify, request, render_template
#from flask_nav import Nav
#from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator
from web_app.models import db
from web_app.routes.home_routes import home_routes
from web_app.routes.company_routes import company_routes
from os import getenv
#from web_app.database import populateDB, \
#                            createAPICallTable, updateDatabase, dbExists
                                

from sqlalchemy import create_engine


#createAPICallTable()

# DATABASE_URI = "sqlite:///DIY_Investment_Primer_dev_DB.db" # using relative filepath
#DATABASE_URI = "sqlite:////Users/Username/Desktop/your-repo-name/web_app_99.db" # using absolute filepath on Mac (recommended)
#DATABASE_URI = "sqlite:///C:\Users\Sean\Documents\GitHub\DIYInvestmentPrimer\\DIY_Investment_Primer_dev_DB.db"
# using absolute filepath on Windows (recommended) h/t: https://stackoverflow.com/a/19262231/670433

#engine = create_engine(os.getenv("DATABASE_URI"), echo=False)
#sqlite_connection = engine.connect()



def create_app():
    application = Flask(__name__)
    app = application
    
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI") 
    db.init_app(app)
    #migrate.init_app(app, db)

    
    #if not dbExists():
    #    populateDB()
    #else:
    #    print("monthly dividend summary already exists!")

    #updateDatabase() # will get moved when we update
   
    app.register_blueprint(home_routes)
    app.register_blueprint(company_routes)
    return app

if __name__ == "__main__":
    my_app = create_app()
    
    
    my_app.run(debug=True)
    