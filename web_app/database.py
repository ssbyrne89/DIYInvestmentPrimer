from sqlalchemy import create_engine
# from web_app.__init__ import DATABASE_URI
import pandas as pd
import json
import requests
import os
from dotenv import load_dotenv
from time import sleep

load_dotenv()

DATABASE_URI = "sqlite:///DIY_Investment_Primer_dev_DB.db"

engine = create_engine(DATABASE_URI, echo=False)
sqlite_connection = engine.connect()
### basic functionality has been worked
### but still needs to be integrated with the rest of the app
### add the chron so that it automatically updates the database monthly




def populateDB():

  if dbExists():
    print("monthly dividend summary already exists!")
    return

  parseDataFromAlphaVAPI()
  # sqlite_table = "month_summary"
  # try:
  #   df.to_sql(sqlite_table,sqlite_connection, if_exists='fail' )
  # except:
  #   print("monthly dividend summary already exists!")

      
  # sqlite_connection.close(df)

def appendDFtoDB(df):

  sqlite_table = "month_summary"
  with engine.connect() as sqlite_connection:
    df.to_sql(sqlite_table,sqlite_connection, if_exists='append')
  

def parseDataFromAlphaVAPI():

  # This function initializes the db. it runs only once!
  SandP500 = pd.read_csv('../DIYInvestmentPrimer/SandP_500_companies.csv')
  trimmedSP500 = SandP500[['Symbol', 'Security', 'Date first added']]

  allCompany_df = pd.DataFrame([[0, 0, 0, 0,0,0, 0, "0", "0", 0, 0]],
                                columns=['1. open', '2. high', '3. low', '4. close', '5. adjusted close',
                                          '6. volume', '7. dividend amount', 'Company_Ticker', 'Company_Name', 'month', 'year'])

  i = 0
  startDFIndex = 1
  
  #for symbol in chunker(lstOFa, 1):
  for symbol in trimmedSP500["Symbol"][:16]:

    if i <= 250:
      APIKEY = os.getenv("APIKEY1")
    else:
      APIKEY = os.getenv("APIKEY2")

    div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey={APIKEY}"
    # div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=abc123"
    parsed_divs = json.loads(requests.get(div_monthly_summary).text) 
  
    ### make a row for each date in the 'Monthly Adjusted Time Series' with the
    ### dividend amount as the entry
    """div_dates = list(parsed_divs.items())
    date_cols = list(div_dates[1][1].keys())"""
    
    monthly_time_series_df = pd.DataFrame.from_dict(parsed_divs['Monthly Adjusted Time Series'], orient ='index')
    monthly_time_series_df['Company_Ticker'] = symbol
    monthly_time_series_df['Company_Name'] = trimmedSP500['Security'][i]
    monthly_time_series_df['month'] = pd.DatetimeIndex(monthly_time_series_df.index).month
    monthly_time_series_df['year'] = pd.DatetimeIndex(monthly_time_series_df.index).year
    monthly_time_series_df.reset_index(drop=True, inplace=True)
    print(monthly_time_series_df.head(3))
    
    allCompany_df = pd.concat([allCompany_df, monthly_time_series_df]) #


    
    x = i % 5
    if x == 0:
      # at this point the df has 5 companies worth of data
      # I can populate for these companies with append, 
      # then continue loop
      appendDFtoDB(allCompany_df[startDFIndex:])
      startDFIndex = allCompany_df.shape[0]
      sleep(65)
    i += 1
  appendDFtoDB(allCompany_df[startDFIndex:])

def dbExists():

  with engine.connect() as sqlite_connection:
    result = sqlite_connection.execute(''' 
    SELECT count(name) 
    FROM sqlite_master
    WHERE type='table' AND name='month_summary' 
    ''')
    for row in result:
        return row[0]==1
  
  



def updateDatabase():
  # this function does a monthly update of the db
  pass