# web_app/__init__.py

from flask import Flask

from web_app.models import db, migrate
from web_app.routes.home_routes import home_routes
from web_app.routes.company_routes import company_routes

from web_app.database import DATABASE_URI, parseDataFromAlphaVAPI, populateDB, \
                            createAPICallTable
                                

from sqlalchemy import create_engine



# DATABASE_URI = "sqlite:///DIY_Investment_Primer_dev_DB.db" # using relative filepath
#DATABASE_URI = "sqlite:////Users/Username/Desktop/your-repo-name/web_app_99.db" # using absolute filepath on Mac (recommended)
#DATABASE_URI = "sqlite:///C:\Users\Sean\Documents\GitHub\DIYInvestmentPrimer\\DIY_Investment_Primer_dev_DB.db"
# using absolute filepath on Windows (recommended) h/t: https://stackoverflow.com/a/19262231/670433

engine = create_engine(DATABASE_URI, echo=False)
sqlite_connection = engine.connect()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    db.init_app(app)
    migrate.init_app(app, db)

    
    populateDB()
    createAPICallTable()
    
    app.register_blueprint(home_routes)
    app.register_blueprint(company_routes)
    return app

if __name__ == "__main__":
    my_app = create_app()
    

    my_app.run(debug=True)
    