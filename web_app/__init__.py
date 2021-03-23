# web_app/__init__.py

from flask import Flask

from web_app.models import db, migrate
from web_app.routes.home_routes import home_routes
from web_app.routes.company_routes import company_routes

from web_app.database import DATABASE_URI, parseDataFromAlphaVAPI, populateDB

from sqlalchemy import create_engine



# DATABASE_URI = "sqlite:///DIY_Investment_Primer_dev_DB.db" # using relative filepath
#DATABASE_URI = "sqlite:////Users/Username/Desktop/your-repo-name/web_app_99.db" # using absolute filepath on Mac (recommended)
#DATABASE_URI = "sqlite:///C:\Users\Sean\Documents\GitHub\DIYInvestmentPrimer\\DIY_Investment_Primer_dev_DB.db"
# using absolute filepath on Windows (recommended) h/t: https://stackoverflow.com/a/19262231/670433

engine = create_engine(DATABASE_URI, echo=False)
sqlite_connection = engine.connect()



def parseDataFromAlphaVAPI():

  # This function initializes the db.
  # it runs only once!


  # SandP500 = pd.read_csv('/Users/kellycho/Desktop/Repos/DIYInvestmentPrimer/SandP_500_companies.csv')
  SandP500 = pd.read_csv('../DIYInvestmentPrimer/SandP_500_companies.csv')

  trimmedSP500 = SandP500[['Symbol', 'Security', 'Date first added']]

  allCompany_df = pd.DataFrame([[0, 0, 0, 0,0,0, 0, "0", "0", 0, 0]],
                                columns=['1. open', '2. high', '3. low', '4. close', '5. adjusted close',
                                          '6. volume', '7. dividend amount', 'Company_Ticker', 'Company_name', 'month', 'year'])
  i = 0
  #for symbol in chunker(lstOFa, 1):
  for symbol in trimmedSP500["Symbol"][0:250]:
    div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=abc123"

  
    parsed_divs = json.loads(requests.get(div_monthly_summary).text) 
  
    ### make a row for each date in the 'Monthly Adjusted Time Series' with the
    ### dividend amount as the entry
    """div_dates = list(parsed_divs.items())
    date_cols = list(div_dates[1][1].keys())"""
    
    monthly_time_series_df = pd.DataFrame.from_dict(parsed_divs['Monthly Adjusted Time Series'], orient ='index')
    monthly_time_series_df['Company_Ticker'] = symbol
    monthly_time_series_df['Company_name'] = trimmedSP500['Security'][i]
    monthly_time_series_df['month'] = pd.DatetimeIndex(monthly_time_series_df.index).month
    monthly_time_series_df['year'] = pd.DatetimeIndex(monthly_time_series_df.index).year
    monthly_time_series_df.reset_index(drop=True, inplace=True)
    print(monthly_time_series_df.head(1))
    
    allCompany_df = pd.concat([allCompany_df, monthly_time_series_df])

    
    x = i % 5
    if x == 0:
      sleep(65)
    i += 1
  
  return allCompany_df

def populateDB():
    
    df = parseDataFromAlphaVAPI()
    sqlite_table = "month_summary"
    df.to_sql(sqlite_table,sqlite_connection, if_exists='replace' )
    
    sqlite_connection.close()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    db.init_app(app)
    migrate.init_app(app, db)

    populateDB()

    app.register_blueprint(home_routes)
    app.register_blueprint(company_routes)
    return app

if __name__ == "__main__":
    my_app = create_app()
    

    my_app.run(debug=True)
