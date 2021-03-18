from sqlalchemy import create_engine
from web_app.__init__ import DATABASE_URI
import pandas as pd

engine = create_engine(DATABASE_URI, echo=False)

### basic functionality has been worked
### but still needs to be integrated with the rest of the app
### add the chron so that it automatically updates the database monthly

allCompany_df = pd.DataFrame([[0, 0, 0, 0,0,0, 0, "0", "0", 0, 0]],
                               columns=['1. open', '2. high', '3. low', '4. close', '5. adjusted close',
                                        '6. volume', '7. dividend amount', 'Company_Ticker', 'Company_name', 'month', 'year'])
i = 0
#for symbol in chunker(lstOFa, 1):
for symbol in trimmedSP500["Symbol"][0:5]:
  div_monthly_summary = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=abc123"

 
  parsed_divs = json.loads(requests.get(div_monthly_summary).text) 
 
  ### make a row for each date in the 'Monthly Adjusted Time Series' with the
  ### dividend amount as the entry
  """div_dates = list(parsed_divs.items())
  date_cols = list(div_dates[1][1].keys())"""
  
  monthly_time_series_df = pd.DataFrame.from_dict(parsed_divs['Monthly Adjusted Time Series'], orient ='index')
  monthly_time_series_df['Company_ticker'] = symbol
  monthly_time_series_df['Company_name'] = trimmedSP500['Security'][i]
  monthly_time_series_df['month'] = pd.DatetimeIndex(monthly_time_series_df.index).month
  monthly_time_series_df['year'] = pd.DatetimeIndex(monthly_time_series_df.index).year
  monthly_time_series_df.reset_index(drop=True, inplace=True)
  print(monthly_time_series_df.head(3))
  
  allCompany_df = pd.concat([allCompany_df, monthly_time_series_df])

  
  x = i % 5
  if x == 0:
    sleep(65)
  i += 1
 
allCompany_df