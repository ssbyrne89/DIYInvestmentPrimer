from sqlalchemy import create_engine
# from web_app.__init__ import DATABASE_URI
import pandas as pd
import json
import requests
import os

from datetime import datetime

from dotenv import load_dotenv
from time import sleep

load_dotenv()

DATABASE_URI = "sqlite:///DIY_Investment_Primer_dev_DB.db"

engine = create_engine(DATABASE_URI, echo=False)
sqlite_connection = engine.connect()

API_META_DATABASE_URI = "sqlite:///AlphaVApi_meta_DB.db"
engine2 = create_engine(API_META_DATABASE_URI, echo=False)


CREATE_API_META_TABLE = """
CREATE TABLE IF NOT EXISTS api_call(
    id INTEGER PRIMARY KEY,
    company TEXT,
    api_key_id INTEGER,
    date REAL
);
"""

INSERT_API_CALL = """
INSERT INTO api_call (company, date, api_key_id)
VALUES (?,?, ?);
"""


def createAPICallTable():
  with engine2.connect() as conn:
    conn.execute(CREATE_API_META_TABLE)

def logAPICall(symbol, date, logKey):
  with engine2.connect() as conn:
    conn.execute(INSERT_API_CALL, symbol, date, logKey)

def populateDB():

  if dbExists():
    print("monthly dividend summary already exists!")
    return

  parseDataFromAlphaVAPI()
  

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

  for symbol in trimmedSP500["Symbol"][:]:

    logKey = 0
    if (i <= 60) or (i >= 121 and i <= 180) or (i >= 241 and i <= 300) or (i >= 421 and i <= 480):
      APIKEY = os.getenv("APIKEY1")
      logKey = 1
    elif (i >= 61 and i <= 120) or (i >= 181 and i <= 240) or (i >= 361 and i <= 420) or (i >= 481):
      APIKEY = os.getenv("APIKEY2")
      logKey = 2

    div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey={APIKEY}"
    # div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=abc123"

    logAPICall(symbol, datetime.now(), logKey)



    parsed_divs = json.loads(requests.get(div_monthly_summary).text) 

    if encounteredError(parsed_divs):
      i += 1
      continue
    
    
    
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
    WHERE type='table' AND name='month_summary'; 
    ''')
    for row in result:
        return row[0]==1
  
  
def encounteredError(parsedDivs):
  if 'Note' in parsedDivs:
    print("THROTTLED!")
    sleep(65)
    return False

  if 'Error Message' in parsedDivs:
    print("ERROR MESSAGE")
    return True

  return False

def updateDatabase():
  # this function does a monthly update of the db
  pass