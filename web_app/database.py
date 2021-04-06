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
    service_company TEXT,
    service_call TEXT,
    date REAL
);
"""

INSERT_API_CALL = """
INSERT INTO api_call (company, date, api_key_id, service_company, service_call)
VALUES (?,?,?, ?, ?);
"""





def createAPICallTable():
  with engine2.connect() as conn:
    conn.execute(CREATE_API_META_TABLE)


def logAPICall(symbol, date, logKey, company, service):
  with engine2.connect() as conn:
    conn.execute(INSERT_API_CALL, symbol, date, logKey, company, service)
  

def appendDFtoDB(df):
  print(df.head(3))
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

def initializeMonthlySummaryDF():

  SandP500 = pd.read_csv('../DIYInvestmentPrimer/SandP_500_companies.csv')
  # trimmedSP500 = SandP500[['Symbol', 'Security', 'Date first added']]
  
  allCompany_df = pd.DataFrame([[0, 0, 0, 0,0,0, 0, "0", "0", 0, 0]],
                                columns=['open', 'high', 'low', 'close', 'adjusted_close',
                                          'volume', 'dividend_amount', 'Company_Ticker', 
                                          'Company_Name', 'month', 'year'])
  return (allCompany_df, SandP500)


def parseSingleCallFromAlphaVAPI(symbol, logKey):

  if logKey == 0:
    APIKEY = "abc123"
#     user_agent_mac_desktop = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '\
# 'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15'

#     headers = { 'User-Agent': user_agent_mac_desktop}

  elif logKey == 1:
    APIKEY = os.getenv("APIKEY1")
    # test_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    # headers = { 'User-Agent': test_agent}
  else:
    APIKEY = os.getenv("APIKEY2")
    # test_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    # headers = { 'User-Agent': test_agent}

  div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey={APIKEY}"
  
  logAPICall(symbol, datetime.now(), logKey, "ALPHA VANTAGE", "TIME_SERIES_MONTHLY_ADJUSTED")

  parsedCompanyRecord = json.loads(requests.get(div_monthly_summary ).text) # headers=headers

  return parsedCompanyRecord


def companyRecordToDf(parsedCoRecord, companyName, symbol):

    currentCompany_df = pd.DataFrame.from_dict(parsedCoRecord['Monthly Adjusted Time Series'], orient ='index')
    currentCompany_df = currentCompany_df.rename(columns={'1. open':'open',
                                                          '2. high': 'high',
                                                          '3. low': 'low',
                                                          '4. close': 'close',
                                                          '5. adjusted close': 'adjusted_close',
                                                          '6. volume': 'volume',
                                                          '7. dividend amount': 'dividend_amount'})
    
    currentCompany_df['Company_Ticker'] = symbol
    
    
    currentCompany_df['Company_Name'] = companyName
    currentCompany_df['month'] = pd.DatetimeIndex(currentCompany_df.index).month
    currentCompany_df['year'] = pd.DatetimeIndex(currentCompany_df.index).year
    currentCompany_df.reset_index(drop=True, inplace=True)
    
    return currentCompany_df

def getCurrentCompanyDf(companyRecord, currentSymbol, currentIndex):

  allCompany_df, SandP500 = initializeMonthlySummaryDF()

  companyName_con = SandP500.loc[:]['Symbol'] == currentSymbol
  companyName = SandP500[companyName_con]["Security"][currentIndex]

  return companyRecordToDf(companyRecord, companyName, currentSymbol)


def populateDB(): # change name

  # This function initializes the db. it runs only once!

  startDFIndex = 1
  
  allCompany_df, SandP500 = initializeMonthlySummaryDF()
  i = 0

  for symbol in SandP500["Symbol"][:]:

    parsedCompanyRecord = parseSingleCallFromAlphaVAPI(symbol, i%3) 
    
    # Refactor Duplication
    if exceededAPIcallRate(parsedCompanyRecord):
      print("THROTTLED!")
      sleep(65)
      continue

    if encounteredError(parsedCompanyRecord):
      i += 1
      continue
    
    currentCompany_df = getCurrentCompanyDf(parsedCompanyRecord, symbol, i)
    
    allCompany_df = pd.concat([allCompany_df, currentCompany_df])

    # Append df to 
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
  if 'Note' in parsedDivs:
    print(parsedDivs['Note'])
    return True
  return 'Note' in parsedDivs


def encounteredError(parsedDivs):
  if 'Error Message' in parsedDivs:
    print(parsedDivs['Error Message'])
    return True

  return False


def updateDatabase():
  # this function does a monthly update of the db
  # On the 5th of the month, 
  
  if datetime.today().day == 5:

    allCompany_df, SandP500 = initializeMonthlySummaryDF()
    i = 0

    for symbol in SandP500["Symbol"][:]:

      parsedCompanyRecord = parseSingleCallFromAlphaVAPI(symbol, i%3)

      #TODO: Refactor Duplication
      if exceededAPIcallRate(parsedCompanyRecord):
        print("THROTTLED!")
        sleep(65)
        continue

      if encounteredError(parsedCompanyRecord):
        i += 1
        continue

      currentCompany_df = getCurrentCompanyDf(parsedCompanyRecord, symbol, i)


      # this condition doesn't work on Jan of the year (to update Dec of the previous year)
      currentMonth_con = (currentCompany_df['month'] == datetime.today().month) & (currentCompany_df['year'] == datetime.today().year)

      currentCompany_df = currentCompany_df[currentMonth_con]

      # print(currentCompany_df.head())
      appendDFtoDB(currentCompany_df)

      x = i % 5
      if x == 0:
        sleep(61)
      i += 1

def selectLogKey(symbolIndex):
  
  logKey = 0
  if symbolIndex <=175:
    logKey = 0
  elif symbolIndex > 175 and symbolIndex <350:
    logKey = 1
  else:
    logKey = 2
  
  return logKey


# create a list of logKey
# iterate through list 5 times 
# pause for 61 secs
# def newSelectLogKey():
#   keyList = [0, 1, 2]

#   for key in keyList:

  