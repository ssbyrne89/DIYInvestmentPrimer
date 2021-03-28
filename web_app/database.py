from sqlalchemy import create_engine
from sqlalchemy.types import Float, Integer
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
    df.to_sql(sqlite_table,sqlite_connection, if_exists='append',
              dtype={"open": Float(),
                    "high": Float(),
                    "low": Float(),
                    "close": Float(),
                    "adjusted_close": Float(),
                    "volume": Integer(),
                    "dividend_amount": Float(),
                      })
    

def parseDataFromAlphaVAPI():

  # This function initializes the db. it runs only once!
  SandP500 = pd.read_csv('../DIYInvestmentPrimer/SandP_500_companies.csv')
  trimmedSP500 = SandP500[['Symbol', 'Security', 'Date first added']]

  allCompany_df = pd.DataFrame([[0, 0, 0, 0,0,0, 0, "0", "0", 0, 0]],
                                columns=['open', 'high', 'low', 'close', 'adjusted_close',
                                          'volume', 'dividend_amount', 'Company_Ticker', 
                                          'Company_Name', 'month', 'year'])

  i = 0
  startDFIndex = 1
  
  #for symbol in chunker(lstOFa, 1):

  for symbol in trimmedSP500["Symbol"][:]:

    logKey = 0
    if i <=175:
      APIKEY = "abc123"
      logKey = 0

    elif i > 175 and i <350:
      APIKEY = os.getenv("APIKEY1")
      logKey = 1
    else:
      APIKEY = os.getenv("APIKEY2")
      logKey = 2

    div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey={APIKEY}"
    # div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=abc123"

    logAPICall(symbol, datetime.now(), logKey)



    parsed_divs = json.loads(requests.get(div_monthly_summary).text) 

    if exceededAPIcallRate(parsed_divs):
      print("THROTTLED!")
      sleep(65)
      continue

    if encounteredError(parsed_divs):
      i += 1
      continue
    
    
    
    monthly_time_series_df = pd.DataFrame.from_dict(parsed_divs['Monthly Adjusted Time Series'], orient ='index')
    monthly_time_series_df = monthly_time_series_df.rename(columns={'1. open':'open',
                                                                    '2. high': 'high',
                                                                    '3. low': 'low',
                                                                    '4. close': 'close',
                                                                    '5. adjusted close': 'adjusted_close',
                                                                    '6. volume': 'volume',
                                                                    '7. dividend amount': 'dividend_amount'})
    
    monthly_time_series_df['Company_Ticker'] = symbol
    monthly_time_series_df['Company_Name'] = trimmedSP500['Security'][i]
    monthly_time_series_df['month'] = pd.DatetimeIndex(monthly_time_series_df.index).month
    monthly_time_series_df['year'] = pd.DatetimeIndex(monthly_time_series_df.index).year
    monthly_time_series_df.reset_index(drop=True, inplace=True)
    print(monthly_time_series_df.head(3))
    
    allCompany_df = pd.concat([allCompany_df, monthly_time_series_df])


    
    x = i % 5
    if x == 0:
      appendDFtoDB(allCompany_df[startDFIndex:])
      startDFIndex = allCompany_df.shape[0]
      sleep(61)
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
  
def exceededAPIcallRate(parsedDivs):
  if 'Information' in parsedDivs:
    print(parsedDivs['Information'])
    return True
  return 'Note' in parsedDivs

def encounteredError(parsedDivs):
  if 'Error Message' in parsedDivs:
    print(parsedDivs['Error Message'])
    return True

  return False

def updateDatabase():
  # this function does a monthly update of the db
  pass