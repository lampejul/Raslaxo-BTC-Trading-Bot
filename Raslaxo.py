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


import io
import sys
import base64
import hashlib
import hmac
import urllib.request
import time
import requests

import yfinance as yf
import pandas_ta as pta
import ta

import smtplib
import ssl
from email.mime.text import MIMEText

import io
import sys

# To gather the output for the mail: io.StringIO-Objekt, 
output_buffer = io.StringIO()
sys.stdout = output_buffer


# Configure API key (copy/paste from account management)
api_url = "https://api.kraken.com"
api_key = 'insert your key here'
api_sec = 'insert your key here'

#Variables
trade_symbol = 'XXBTZUSD'
leverage = 1
result_is_empty = True
sleep = 0
Typ = "buy"
volume = 0
Paar = "XXBTZEUR"
EUR_balance = 0
BTC_balance = 0 
vol= 0
loop_long = True
loop_short = True
opennet = 0
closednet = 0

#Mail insert your data here:
gesammelter_text = '' #collected text for mail
Tradeentscheidung = '' # Tradedecision
port = 465  # server port (SSL)
smtp = ''  # SMTP server
password = ''  # your password
user = ''  # your username
sender_email = ''  # your mail
receiver_email = ''  # receivers mail
subject = 'RASLAXO is awake..and..fell asleep again'  # your subject


#Functions
def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req

def Datamatrix(df):
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

    print('-Indicators added:')
    print ('-MACD:', df.MACD.iloc[-1], 'signal:', df.signal.iloc[-1], 'K:', df.K.iloc[-1], 'D:', df.D.iloc[-1], 'RSI:', df.rsi.iloc[-1] )
    
            
def getInfo():

    #open Orders    
    resp = kraken_request('/0/private/OpenOrders', {
    "nonce": str(int(1000*time.time())),
    "trades": True
    }, api_key, api_sec)

    #open position
    resp = kraken_request('/0/private/OpenPositions', {
    "nonce": str(int(1000*time.time())),
    "docalcs": True
    }, api_key, api_sec)

    print('The open positions are:', resp.json())

    #Get Trade Balance
    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_sec)

    print('The current balance is:', resp.json()) 
    time.sleep(3)

def TradeLong(Typ, volume, Paar):
    print('addorder...')
    resp = kraken_request('/0/private/AddOrder', {
    "nonce": str(int(1000*time.time())),
    "ordertype": "market",
    "type": Typ,
    "volume": volume,
    "pair": Paar,
    "validate": False,
    }, api_key, api_sec)

    subject = 'RASLAXO WOKE UP ... HE TRADED!!!' 

    print(resp.json())  

def Trade(Typ, volume, Paar, leverage):
    print('addorder...')
    resp = kraken_request('/0/private/AddOrder', {
    "nonce": str(int(1000*time.time())),
    "ordertype": "market",
    "type": Typ,
    "volume": volume,
    "pair": Paar,
    "leverage": leverage,
    "validate": False,
    }, api_key, api_sec)

    subject = 'RASLAXO WOKE UP ... HE TRADED!!!' 

    print(resp.json())

def get_position():
    global result_is_empty
    global vol
    
    resp_positions = kraken_request('/0/private/OpenPositions', {
    "nonce": str(int(1000*time.time())),
    "docalcs": True
    }, api_key, api_sec)

    result_is_empty = not resp_positions.json()['result']

    #volume needed for short
    if 'result' in resp_positions.json() and resp_positions.json()['result']:
        
        vol = resp_positions.json()['result'][next(iter(resp_positions.json()['result']))]['vol']
    else:
        vol = 0   
        
    print('-Current Volume in Short Position:', vol) 

def Balance():
    global BTC_balance
    global EUR_balance

    resp_balance = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_sec)
    BTC_balance = float(resp_balance.json()['result']['XXBT'])
    EUR_balance = float(resp_balance.json()['result']['ZEUR'])
    print('-Current Balance|   BTC:',float(BTC_balance),' | ','EUR:', float(EUR_balance)  )
    return BTC_balance and EUR_balance

def get_ask_price():
    resp_BTC_price = requests.get('https://api.kraken.com/0/public/Ticker?pair=XXBTZEUR')
    
    try:
        response_data = resp_BTC_price.json() 
        ask_price = float(response_data['result']['XXBTZEUR']['a'][0])
        return ask_price
    except (KeyError, ValueError):
        return None



#MAIN: The Heart of the Trading Bot:

print('Zzzzzzzzzzzzzzzzz ...... RASLAXO woke up!')

try:
    #Get data
    print('Get data for dataframe', end='')
    df = yf.download('BTC-USD', start='2009-03-01')
    Datamatrix(df)
    df.add
    time.sleep(sleep)
   
    while loop_long or loop_short:
        print('<<<<<<<<<<<LOOP>>>>>>>>>>')
        time.sleep(1)
       
        Balance()
        get_position()
        BTC_WertEUR = (EUR_balance / (get_ask_price() * 1.00005)) #1.00005 to buy with a value under the current balance, can/ should be adjusted
        print('-BTC/EUR',  (get_ask_price() * 1.00005))
        print('-----------------------')
        
        
        #Long Loop:      
        if result_is_empty and loop_long:  
            print('----------LONG------------')  
            loop_long = False
            if float(BTC_balance) < 0.0001:
                try: 
                    print('Buy Decision ... ', end='')
                    time.sleep(sleep)
                    if ((df.MACD > df.signal) & (df.rsi>90)).iloc[-1]: #Strategy Buy/Long
                        TradeLong("buy", float(BTC_WertEUR), "XXBTZEUR")
                        loop_short = False
                        Tradeentscheidung = 'In Long Position' + "\n"
                    else:
                        print('No Trade')
                        Tradeentscheidung = 'No Tade' + "\n"
                except Exception as error:
                    print('Failed (%s)' % error)
            elif float(BTC_balance) >= 0.0001: 
                try: 
                    print('Sell Decision ... ', end='')
                    time.sleep(sleep)
                    if ((df.MACD < df.signal)).iloc[-1]: # Strategy End Buy/Long
                        TradeLong("sell", float(BTC_balance), "XXBTZEUR")
                        print('Successfully Bitcoin sold')
                        Tradeentscheidung = 'Successfully Bitcoin sold' + "\n"
                        time.sleep(sleep*4)
                    else:
                        print('Bitcoin Position not ended')
                        loop_short = False
                except Exception as error:
                    print('Failed (%s)' % error)

        #Short Loop
        elif ((float(BTC_balance) < 0.00001) & (float(EUR_balance) > 3)) and loop_short: 
            print('---------SHORT---------')
            print('SHORT - Decision ...: ', end='')
            loop_short = False
            if  (result_is_empty):
                try: 
                    if ((df.D > 90) & (df.D>df.K) & (df.MACD < df.signal)).iloc[-1]:  #Strategy Short
                        Trade("sell", float(BTC_WertEUR), "XXBTZEUR", 2)
                        print('Successfully in Short')
                        loop_long = False
                        Tradeentscheidung = 'Successfully in Short' + "\n"
                    else:
                        print('No Trade')
                        Tradeentscheidung = 'No Shorttrade' + "\n"
                except Exception as error:
                    print('Failed (%s)' % error)
            elif (not result_is_empty): 
                try: 
                    if (((df.MACD > df.signal) & (df.D<df.K)).iloc[-1]): #Strategy End short
                        Trade("buy", float(vol), "XXBTZEUR", 2)
                        print('Successfully Short ended')
                        Tradeentscheidung = 'Successfully short ended' + "\n"
                    else:
                        print('Short Trade not ended')
                        Tradeentscheidung = 'Short Trade not ended' + "\n"
                        loop_long = False
                except Exception as error:
                    print('Failed (%s)' % error)
        else:
            print("No Trade evaluated. Please check manually.")
            Tradeentscheidung = 'No Trade evaluated. Please check manually.' + "\n"
            loop_long = False
            loop_short = False

    time.sleep(sleep)
    print('<<<<<<<<<<<<Information>>>>>>>>>>>>>>>')
    getInfo()
    print('-----------------------')
    print('-----------------------')
    time.sleep(sleep)
except KeyboardInterrupt:
    sys.exit(0)
except Exception as error:
    print('Error (%s)' % error)

print('Zzzzzzzzzzzzzzzzz RASLAXO is sleeping again...')

# Recreate the standard output
sys.stdout = sys.__stdout__

# get the catched text
gesammelter_text = output_buffer.getvalue()

# show the text
print("Gesammelter Text:")
print(gesammelter_text)

# The Mail message
message = MIMEText(gesammelter_text, 'plain')
message['Subject'] = subject
message['From'] = sender_email
message['To'] = receiver_email


 #Send the info per Mail      

with smtplib.SMTP_SSL(smtp, port, context=ssl.create_default_context()) as server:
    server.login(user, password)
    server.sendmail(sender_email, receiver_email, message.as_string())

print('E-Mail sent')