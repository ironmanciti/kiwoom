# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 17:46:02 2018

@author: trimu
"""

import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

def getStock(symbol):
    df = pd.read_csv('data\\' + symbol + '.csv', index_col='Date')
    df = df[['Adj Close']]

    return df

def addFeatures(symbol, df, n, delta):

    df['{}_Return'.format(symbol)] = df['Adj Close'].pct_change()  # multiple day return

    for i in range(0, n):
        df['{}_Lag_'.format(symbol) + str(i+1)] =  df['Adj Close'].shift(i+1)

    for i in range(0, n):
        df['{}_Lag_'.format(symbol) + str(i+1)] = df['{}_Lag_'.format(symbol) + str(i+1)].pct_change()

    df['{}_Rolling_{}'.format(symbol, str(delta))] = pd.Series.rolling(df['{}_Return'.format(symbol)], window=delta).mean()

    return df

def getStockData(symbol, n, delta):

    df = getStock(symbol)

    df = addFeatures(symbol, df, n, delta)

    return df
import numpy
def perform_training(method, X_train, y_train, X_test, y_test, n, delta, threshold):

    if method == 'LR':
        model = LogisticRegression()
    elif method == 'LDA':
        model = LDA()
    elif method == 'QDA':
        model = QDA()
    elif method == 'RF':
        model = RandomForestClassifier(n_estimators=1000, n_jobs=-1)
    elif method == 'KNN':
        model = KNeighborsClassifier()
    elif method == 'ADA':
        model = AdaBoostClassifier()
    elif method == 'GTB':
        model = GradientBoostingClassifier(n_estimators=100)
    else:
        print('Invalid method', method)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    hit_rate = (sum(y_pred == y_test.iloc[:,0]))/len(y_pred)
    print('n= {}, delta= {}, method= {} hit_rate= {:.4f}'.format(n, delta, method, hit_rate))

    fname_out = None
    if hit_rate > threshold:

        fname_out = '{}-{}.pickle'.format(method, str(datetime.now().date()))
        with open('pickle\\' + fname_out, 'wb') as f:
            pickle.dump(model, f)

    return hit_rate, fname_out


def make_data(n, delta):
    
    adjusted_df = []

    for symbol in datasets:
        df = getStockData(symbol, n, delta)
        adjusted_df.append(df)

    concat_df = pd.concat(adjusted_df, axis=1)

    concat_df.dropna(inplace=True)

    for symbol in datasets:
        #concat_df.loc[(concat_df['{}_Return'.format(symbol)] == 0), '{}_Return'.format(symbol)] = 0.0001
        for k, v in enumerate(concat_df['{}_Return'.format(symbol)]):
            if (abs(v) < 0.0001):
                concat_df['{}_Return'.format(symbol)][k] = 0.0001


    concat_df["Direction"] = np.sign(concat_df['SPY_Return'])

    lag_cols = []
    for symbol in datasets:
        for i in range(n):
            lag_cols.append(symbol + "_Lag_" + str(i+1))
        lag_cols.append('{}_Rolling_{}'.format(symbol, str(delta)))

    X = concat_df[lag_cols]
    y = concat_df[["Direction"]]

    start_test = '2014-01-01'
    start_validation = '2016-01-01'
    X_train = X.loc[X.index < start_test, :]
    X_test = X.loc[(X.index > start_test) & (X.index < start_validation), :]
    X_validation = X.loc[X.index > start_validation, :]
    y_train = y.loc[y.index < start_test, :]
    y_test  = y.loc[(y.index > start_test) & (y.index < start_validation), :]
    y_validation  = y.loc[y.index > start_validation, :]

    return X_train, X_test, X_validation, y_train, y_test, y_validation

datasets = ['AXJO', 'DJI', 'FCHI', 'HSI', 'N225', 'IXIC', 'GDAXI','SPY']
output = []
pickle_out = []
cols = ['n','delta','method','hit rate']
threshold = 0.8

for n in range(2,4):

    for delta in range(2,4):

        X_train, X_test, X_validation, y_train, y_test, y_validation = make_data(n, delta)

        for method in ['LR','LDA','QDA','RF', 'KNN','ADA','GTB']:
            hit_rate, fname_out = perform_training(method, X_train, y_train, X_test, y_test, n, delta, threshold)
            output.append([n, delta, method, hit_rate])
            if fname_out:
                pickle_out.append(fname_out)

output = pd.DataFrame(output,columns=cols)

for file in pickle_out:
    with open('pickle\\' + file, 'rb') as f:
        clf = pickle.load(f)

    y_pred = clf.predict(X_validation)

    hit_rate = (sum(y_pred == y_validation.iloc[:,0]))/len(y_pred)
    print('file = {} hit_rate= {:.4f}'.format(file, hit_rate)) 
