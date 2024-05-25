#Disclaimer: This is not an investment advice and is for educational purposes only! 
#Cryptocurrency and automated trading is bearing a high amount of risk which might result in a total loss of your invested capital.


# MIT License
# 
# Copyright (c) 2024 lampejul
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
import sys
import base64
import hashlib
import hmac
import urllib.request
import time
import requests

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as pta
from datetime import datetime
pd.options.mode.chained_assignment = None
import numpy as np
import ta

import smtplib
import ssl
from email.mime.text import MIMEText


import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as pta
from datetime import datetime
pd.options.mode.chained_assignment = None
import numpy as np
import ta



df = yf.download('BTC-USD', start='2009-03-01')


def Datamatrix(df):
    
    #Indicators
    df['price'] = df.Open.shift(-1)
    df['EMA12'] = df.Close.ewm(span=84).mean(63)
    df['EMA26'] = df.Close.ewm(span=182).mean(63)
    df['EMA9'] = df.Close.ewm(span=9).mean()
    df['EMA12'] = df.Close.ewm(span=12).mean()

    df['K'] = ta.momentum.stoch(df.High,df.Low, df.Close, window=2000, smooth_window=600)
    df['D'] = df['K'].rolling(35).mean()

    df['MACD'] = df.EMA12 - df.EMA26
    df['signal'] = df.MACD.ewm(span=82).mean(82)

    df['rsi'] = pta.rsi(df['Close'], length = 6)
    
    #Strategy:
    df['Buy'] = (df.MACD > df.signal) & (df.rsi>90) 
    df['Sell'] = (df.MACD < df.signal)
    df['Short'] = (df.D > 80) & (df.D>df.K) & (df.MACD < df.signal)
    df['Endshort'] = (df.MACD > df.signal) & (df.D<df.K)
    
    
    print('indicators added')
    print (df)

Datamatrix(df)

in_position = False
in_positionshort = False

buys,sells = [],[]
buydates, selldates = [],[]

shortin, shortout =[],[]
shortindate, shortoutdate = [],[]

for index, row in df.iterrows():
    if not in_positionshort:
        if row.Short:
            shortin.append(row.price)
            shortindate.append(index)
            in_positionshort = True
        
    if in_positionshort:
        
        if row.Endshort:
            shortout.append(row.price)
            shortoutdate.append(index)
            in_positionshort= False
            
shorttrades = pd.DataFrame( [shortin,shortindate, shortout, shortoutdate], index=['Shorts','Shortindate', 'Shortout', 'Shortoutdate'])
shorttrades= shorttrades.T
shorttrades['profit'] = (shorttrades.Shorts - shorttrades.Shortout)
shorttrades['relprofit'] = (shorttrades.Shorts - shorttrades.Shortout) / shorttrades.Shorts
print(shorttrades)
print('The sum of the relative profit of the shortstrategy is:',sum(shorttrades.relprofit))

for index, row in df.iterrows():
    if not in_position:
        if row.Buy:
            buys.append(row.price)
            buydates.append(index)
            in_position = True
        
    if in_position:
        
        if row.Sell:
            sells.append(row.price)
            selldates.append(index)
            in_position= False
            
trades = pd.DataFrame( [buys,buydates, sells, selldates], index=['Buys','Buydate', 'Sells', 'Selldate'])
trades=trades.T

trades['profit'] = (trades.Sells - trades.Buys)
trades['relprofit'] = (trades.Sells - trades.Buys)/ trades.Buys

print(trades)
print('The sum of the relative profits of the buy stategy is:',sum(trades.relprofit))

plt.plot(df.signal, label='signal', color='red')
plt.plot(df.MACD, label='MACD', color='green')
plt.plot(df.rsi, label='rsi', color='blue')
plt.legend()
plt.show()

plt.plot(df.K, label='%K', color='orange')
plt.plot(df.D, label='%D', color='purple')
plt.legend()
plt.show()

plt.figure(figsize=(12,4))
plt.scatter(df.loc[buydates].index, df.loc[buydates] ['Close'], marker="^", color='green')
plt.scatter(df.loc[selldates].index, df.loc[selldates] ['Close'], marker="v", color='red')
plt.plot(df.Close, label='BTC Close', color='k')
plt.legend()
plt.show()


plt.figure(figsize=(12,4))
plt.scatter(df.loc[shortindate].index, df.loc[shortindate] ['Close'], marker="v", color='orange')
plt.scatter(df.loc[shortoutdate].index, df.loc[shortoutdate] ['Close'], marker="^", color='purple')
plt.plot(df.Close, label='BTC Close', color='k')
plt.legend('Sellstrategy')
plt.show()

