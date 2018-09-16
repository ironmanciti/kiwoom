# -*- coding: utf-8 -*-
"""

getStock() : marketcandle table read

addFeatures() : 1. daily return 의 pct_change() 를 symbol_Return column 에 추가
    2. lag 수 만큼 'Adj Close' 를 shift 한 symbol_Lag_ column 추가
    3. symbol_Lag_  의 pct_change 로 symbol_lag_ value pct_change
    4. symbol_Rolling_delta 의 이동 평균 추가

make_data() : 1. 전체 symbols 를 모두 concat 한 concat_df  생성
    2. dropna
    3. symbol_Retun 의 절대값이 < 0.0001 이면 symbol_Retun = 0.0001 assign
    4. SPY 의 상승, 하락을 맞추는 문제이므로 concat_df 의 Direction 에 SPY_Return 의 sign assign
    5. X, y 를 start_test, start_validation 날자에 따라 train, test, validation set 으로 구분
"""

import pandas as pd
import numpy as np
import pandas
from pandas import Series
import pickle
from datetime import datetime
import sys
sys.path.append('../lib/')
from dbConnect import *

def getStock(code, end_date):
    df = pd.read_sql("SELECT * from marketcandle where code ='" + code + "' and date < '" + \
                                                                                end_date + "'" , conn)
    df.loc[:,'date'] = pd.to_datetime(df.loc[:,'date'])
    df.set_index('date', inplace=True)

    return df

def addFeatures(df, win_K, win_CCI, win_R, lags, RSI_span, win_ma):
    df["returns"] = df["close"].pct_change()
    df['returns'] = df["returns"].shift(-1)

    #--- Stochastic %K
    tmpdf = df.copy(deep=True)
    tmpdf['H14'] = Series.rolling(tmpdf['high'], window=win_K).max()
    tmpdf['L14'] = Series.rolling(tmpdf['low'], window=win_K).min()
    df['%K'] = (tmpdf['close'] - tmpdf['L14']) / (tmpdf['H14'] - tmpdf['L14']) * 100
    df['%D'] = Series.rolling(df['%K'], window=3).mean()
    df['slow%D'] = Series.rolling(df['%D'], window=3).mean()

    #--- Accumulation Distribution Oscillator (ADO)
    tmpdf = df.copy(deep=True)
    tmpdf['Ct-1'] = tmpdf['close'].shift(1)
    df['ADO'] = (tmpdf['high'] - tmpdf['Ct-1']) / (tmpdf['high'] - tmpdf['low'])

    #--- CCI(Commodity Channel Index)
    tmpdf = df.copy(deep=True)
    tmpdf['M'] = (tmpdf['high'] + tmpdf['low'] + tmpdf['close']) / 3
    tmpdf['SM'] = tmpdf['M'].rolling(window=win_CCI).mean()
    tmpdf['D'] =  (tmpdf['M'] - tmpdf['SM']).abs().rolling(window=win_CCI).mean()
    df['CCI'] = (tmpdf['M'] - tmpdf['SM']) / (0.015 * tmpdf['D'])

    #--- Larry William's R%
    tmpdf = df.copy(deep=True)
    tmpdf['Hr'] = Series.rolling(tmpdf['high'], window=win_R).max()
    tmpdf['Lr'] =  Series.rolling(tmpdf['low'], window=win_R).min()
    df['%R'] = 100 * (tmpdf['Hr'] - tmpdf['close']) / (tmpdf['Hr'] - tmpdf['Lr'])

    #--- MACD
    tmpdf = df[['close']].copy(deep=True)
    tmpdf['ewma12'] = Series.ewm(tmpdf['close'], span=12).mean()
    tmpdf['ewma26'] = Series.ewm(tmpdf['close'], span=25).mean()
    df['MACD'] = tmpdf['ewma12'] - tmpdf['ewma26']

    #--- Momentum
    tslag = df[['close']].copy(deep=True)
    last_lag = 'close'
    for i in range(0, lags):
        tslag["Lag_" + str(i+1)] = tslag["close"].shift(i+1)
        last_lag = "Lag_" + str(i+1)

    df['momentum'] = tslag['close'] - tslag[last_lag]

    #--- ROC : Price Rate Of Change
    df['ROC'] = tslag['close'] / tslag[last_lag] * 100

    #--- RSI (Relative Strength Index)
    tmpdf = df[['close']].copy()

    delta = tmpdf['close'].diff()
    delta = delta[1:]

    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0.0001

    roll_up = up.ewm(span=RSI_span).mean()
    roll_down = down.abs().ewm(span=RSI_span).mean()

    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    df['RSI'] = RSI

    #--- Simple Moving Average
    df['SMA'] = Series.rolling(df['close'], window=win_ma).mean()
    df['WMA'] = Series.ewm(df['close'], span=win_ma).mean()

    return df

def make_data(end_date, start_test, start_validation, code, win_K, win_CCI, win_R, lags, RSI_span, win_ma):

    df = getStock(code, end_date)
    df = addFeatures(df, win_K, win_CCI, win_R, lags, RSI_span, win_ma)

    df.dropna(inplace=True)
    df["Direction"] = np.sign(df["returns"])

    X = df.drop(columns=['returns', 'Direction'])
    y = df.loc[:,"Direction"]

    # Create training and test sets
    X_train = X[X.index < start_test]
    X_test = X[(X.index >= start_test) & (X.index < start_validation)]
    X_validation = X[X.index >= start_validation]
    y_train = y[y.index < start_test]
    y_test = y[(y.index >= start_test) & (y.index < start_validation)]
    y_validation  = y[y.index >= start_validation]

    return X_train, X_test, X_validation, y_train, y_test, y_validation
