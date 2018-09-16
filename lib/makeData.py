# -*- coding: utf-8 -*-
"""

getStock() : csv file 들을 읽어서 'Adj Close' column 만 df 로 Returns

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
from datetime import datetime

def getStock(data_path, symbol):
    df = pd.read_csv(data_path + symbol + '.csv', index_col='Date')
    df = df[['Adj Close']]

    return df

def addFeatures(symbol, df, lag, delta):

    df['{}_Return'.format(symbol)] = df['Adj Close'].pct_change()  # multiple day return

    for i in range(0, lag):
        df['{}_Lag_'.format(symbol) + str(i+1)] =  df['Adj Close'].shift(i+1)

    for i in range(0, lag):
        df['{}_Lag_'.format(symbol) + str(i+1)] = df['{}_Lag_'.format(symbol) + str(i+1)].pct_change()

    df['{}_Rolling_{}'.format(symbol, str(delta))] \
                    = pd.Series.rolling(df['{}_Return'.format(symbol)], window=delta).mean()

    return df

def make_data(lag, delta, start_test, start_validation, data_path, symbols):

    adjusted_df = []

    for symbol in symbols:
        df = getStock(data_path, symbol)
        df = addFeatures(symbol, df, lag, delta)
        adjusted_df.append(df)

    concat_df = pd.concat(adjusted_df, axis=1)

    concat_df.dropna(inplace=True)

    for symbol in symbols:
        for k, v in enumerate(concat_df['{}_Return'.format(symbol)]):
            if (abs(v) < 0.0001):
                concat_df['{}_Return'.format(symbol)][k] = 0.0001

    concat_df["Direction"] = np.sign(concat_df['SPY_Return'])

    lag_cols = []
    for symbol in symbols:
        for i in range(lag):
            lag_cols.append('{}_Lag_'.format(symbol) + str(i+1))
        lag_cols.append('{}_Rolling_{}'.format(symbol, str(delta)))

    X = concat_df[lag_cols]
    y = concat_df[["Direction"]]

    X_train = X.loc[X.index < start_test, :]
    X_test = X.loc[(X.index >= start_test) & (X.index < start_validation), :]
    X_validation = X.loc[X.index >= start_validation, :]
    y_train = y.loc[y.index < start_test, :]
    y_test  = y.loc[(y.index >= start_test) & (y.index < start_validation), :]
    y_validation  = y.loc[y.index >= start_validation, :]

    return X_train, X_test, X_validation, y_train, y_test, y_validation
