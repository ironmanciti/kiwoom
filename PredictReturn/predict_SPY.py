# -*- coding: utf-8 -*-
"""
lags - shift 할 일자의 수. Adj Close 의 몇일치 pct_change 를 feature 로 추가할 것인지 결정
delta - 이동평균 일자
threshold - test set 의 hit_rate 중 pickle 로 저장할 threshold

backtest 에서 사용할 highest_validation_model 을 model_for_backtest.picke 로 저장

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

import sys
sys.path.append('../lib/')
from makeData import *

def perform_training(method, X_train, y_train, X_test, y_test, lag, delta, threshold):

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

    model.fit(X_train,y_train.values.ravel())

    y_pred = model.predict(X_test)

    hit_rate = (sum(y_pred == y_test.iloc[:,0]))/len(y_pred)

    model_dict = {}

    model_dict["method"] = method
    model_dict["model"] = model
    model_dict["lag"] = lag
    model_dict["delta"] = delta

    return hit_rate, model_dict

if __name__ == '__main__':
    symbols = ['^AXJO', '^DJI', '^FCHI', '^HSI', '^N225', '^IXIC', '^GDAXI','SPY']
    start_test = '2014-01-01'      # 2014,1,1 이전 data 는 training set
    start_validation = '2016-01-01'    # 2014,1,1 - 2016,1,1 data 는 test set, 그 이후는 validation set
    data_path = '..\\dataModeling\\'   # Training/Test/validation dataset folder
    output_path = '..\\dataOutput\\'   # output pickle file 및 csv file output folder
    lags = 10  # n + 1                  # 몇일 전 까지 예측에 포함할 것인지 time lag
    deltas = 8 # delta + 1             # 이동평균선 window
    threshold = 0.8                    # test set 에서 threshold 미달한 model 은 validation set 평가에서 탈락

    cols = ['labs','delta','method','hit rate']    # dataOutput csv file header
    output = []

    for lag in range(2, lags):         # 최소 2 일 이전부터 예측에 감안

        models_over_threshold = []

        for delta in range(2, deltas):  # 2 일 이동 평균 이상

            X_train, X_test, X_validation, y_train, y_test, y_validation \
                = make_data(lag, delta, start_test, start_validation, data_path, symbols)

            for method in ['LR','LDA','QDA','RF', 'KNN','ADA','GTB']:    # LogisticRegression models
                hit_rate, model_dict = \
                        perform_training(method, X_train, y_train, X_test, y_test, lag, delta, threshold)

                output.append([lag, delta, method, hit_rate])

                if hit_rate > threshold:
                    models_over_threshold.append(model_dict)
                    print('lag= {}, delta= {}, method= {} training hit_rate= {:.4f}'\
                              .format(lag, delta, method, hit_rate))

        highest_validation_model = {'hit_rate': 0, 'picke_model': ''}

        for model in models_over_threshold:

            clf = model["model"]

            y_pred = clf.predict(X_validation)

            hit_rate = (sum(y_pred == y_validation.iloc[:,0]))/len(y_pred)

            if hit_rate > highest_validation_model['hit_rate']:
                highest_validation_model['hit_rate'] = hit_rate
                highest_validation_model['picke_model'] = model;

            print('method = {} validation hit_rate= {:.4f}'.format(model['method'], hit_rate))

    print("Highest_validation_model's hit rate = {}, method = {}"\
            .format(highest_validation_model['hit_rate'], highest_validation_model['picke_model']['method']))

    #------ backtest 에 사용할 최종 model 저장
    fname_out = '{}-{}-{}-{}_model_for_backtest.pickle'.format(highest_validation_model['picke_model']['method'],\
                                            str(datetime.now().date()), lag, delta)
    with open(output_path + fname_out, 'wb') as f:
        pickle.dump(highest_validation_model['picke_model'], f)

    #------- save all results -------------
    output = pd.DataFrame(output,columns=cols)
    fname = '{}-{}-{}.csv'.format(str(datetime.now().date()), lags, deltas)
    output.to_csv(output_path + fname)
