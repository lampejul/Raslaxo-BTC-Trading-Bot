
# RASLAXO: THE RASPI BTC TRADING BOT  
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)



## Description 
Most of the current trading bots are trading on shortterm intraday cycles. These daytrading bots have the disadvantage of high fees and high tax payments. Aim of this project was to create a longterm trading bot which is evaluating trading decision only once per day, done with a raspberry pi. The Trading results are send by mail. So instead of reviewing codes and trading results, the trading decision is sent to you directly. 

    Technical framework summarized:
    -Programming Language: Python
    -Yahoo finance used as input for the stock data
    -Kraken with its Kraken API is used as the Trading exchange
      - Kraken Pro Account needed
    -An E-Mail is send after each trading decision
    -Program can be executed an an Raspberry Pi using crontab

## Trading Strategy
Before programming the Strategie.py file, I searched for the most relevant indicators for volatile stocks/asssets like bitcoin and analyzed them in different cycles. Afterwards the indicators were programmed in the strategie.py file and tweaked to get the best result on the profit on BTC since 2009 and have a "risk stabiity" on the future. Please note that the historic dates can not be used to predict the future. Further notes can be found in the disclaimer below.

         Indicators used:
         df['price'] = df.Open.shift(-1)
         df['EMA12'] = df.Close.ewm(span=84).mean(63)
         df['EMA26'] = df.Close.ewm(span=182).mean(63)
         df['EMA9'] = df.Close.ewm(span=9).mean()
         df['EMA12'] = df.Close.ewm(span=12).mean()

         df['K'] = ta.momentum.stoch(df.High,df.Low, df.Close, window=2000,smooth_window=600)
         df['D'] = df['K'].rolling(35).mean()

         df['MACD'] = df.EMA12 - df.EMA26
         df['signal'] = df.MACD.ewm(span=82).mean(82)

         df['rsi'] = pta.rsi(df['Close'], length = 6)

         Strategy:
         Buying if MACD is over the signal line and RSI>90
         Buy: (df.MACD > df.signal) & (df.rsi>90) 
         Sell: (df.MACD < df.signal)
         Short: (df.D > 80) & (df.D>df.K) & (df.MACD < df.signal)
         Endshort: (df.MACD > df.signal) & (df.D<df.K)

The historic trading results are plotted in the stategie.py. I additionally added the historic diagrams with the displayed strategy as a pdf in the project. These show that the strategy, based on the historic dates, is highly profitable.



## Raspberry pi automated with crontab
I am using the Raspberry Pi 3B. But any other Raspberry should be sufficient too. The raspberry turns on with a time switch and runs the raslaxo.py program on startup with crontab. Here you can find how this is done: https://raspberrypi.stackexchange.com/questions/122172/start-python-script-on-startup


## Dependencies

This project uses the following libraries and modules:

- **Python Standard Library modules**: Covered by the Python Software Foundation License.
  - `io`
  - `sys`
  - `base64`
  - `hashlib`
  - `hmac`
  - `urllib.request`
  - `time`
  - `ssl`
  - `smtplib`
  - `email.mime.text`
  - `datetime`

- **Third-Party Libraries**:
  - **`requests`**: Licensed under the Apache License 2.0.
  - **`yfinance`**: Licensed under the MIT License.
  - **`matplotlib`**: Licensed under the Python Software Foundation License (similar to BSD).
  - **`pandas`**: Licensed under the BSD 3-Clause License.
  - **`pandas_ta`**: Licensed under the MIT License.
  - **`numpy`**: Licensed under the BSD 3-Clause License.
  - **`ta`**: Licensed under the MIT License.
## Acknowledgements

 - [Algovibes Youtube Channel](https://www.youtube.com/@Algovibes)



## Disclaimer

This is not an investment advice and is for educational purposes only! 
Cryptocurrency and automated trading is bearing a high amount of risk which might result in a total loss of your invested capital.

This was a project for me to learn and get better in python, technical analysis and raspberry pis! So, no guarantee of completeness and accuracy. Rather I would be happy for your feedback on improvements.
