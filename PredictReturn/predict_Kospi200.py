# -*- coding: utf-8 -*-
"""
KOSPI200 의 다음날 등락 알아 맞추기
lags - RSI 의 average gain 과 average loss 계산 기간
wink - 이동평균 일자

threshold - test set 의 hit_rate 중 pickle 로 저장할 threshold

backtest 에서 사용할 highest_validation_model 을 model_for_backtest.picke 로 저장

@author: trimu
"""

import pandas as pd
import numpy as np
import pandas
from pandas import Series
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
from makeKospi200Data import *

def perform_training(threshold, method, X_train, y_train, X_test, y_test, lag, wink):

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

    hit_rate = (sum(y_pred == y_test))/len(y_pred)

    model_dict = {}

    model_dict["method"] = method
    model_dict["model"] = model
    model_dict["lag"] = lag
    model_dict["win_K"] = wink
    model_dict["win_CCI"] = win_CCI
    model_dict["win_R"] = win_R
    model_dict["RSI_span"] = RSI_span
    model_dict["win_ma"] = win_ma

    return hit_rate, model_dict

if __name__ == '__main__':
    code = "201"
    end_date = '2016-12-31'    # marketcandle table 에서 가져올 end date, 이후 date 는 backtest 용
    start_test = '2013-01-01'  # 이전 일자는 training set, 이후는 test set
    start_validation = '2015-01-01'    # 2013-01-01 ~ 2015-01-01  test set, 2015-01-01 ~ 2016-12-31 은 validation
    output_path = '..\\dataOutput\\'   # output pickle file 및 csv file output folder

    win_K = 14                         # %K window
    win_CCI = 20                       # CCI window
    win_R = 7                          # %R window
    lags = 10                          # momentum 과 ROC 의 비교 기간
    RSI_span = 14                      # RSI 의 average gain 과 average loss 계산 기간
    win_ma = 10                        # moving average window

    threshold = 0.5                    # test set 에서 threshold 미달한 model 은 validation set 평가에서 탈락

    # dataOutput csv file header
    cols = ['win_K', 'win_CCI', 'win_R', 'lags', 'RSI_span', 'win_ma', 'method', 'hit_rate']

    output = []
    
    highest_validation_model = {'hit_rate': 0, 'picke_model': ''}

    for lag in range(3, lags):

        models_over_threshold = []

        for wink in range(13, win_K):

            X_train, X_test, X_validation, y_train, y_test, y_validation = \
            make_data(end_date, start_test, start_validation, code, wink, win_CCI, win_R, lag, RSI_span, win_ma)

            for method in ['LR','LDA','QDA','RF', 'KNN','ADA','GTB']:    # LogisticRegression models
                hit_rate, model_dict = \
                    perform_training(threshold, method, X_train, y_train, X_test, y_test, lag, wink)

                output.append([win_K, win_CCI, win_R, lags, RSI_span, win_ma, method, hit_rate])

                if hit_rate > threshold:
                    models_over_threshold.append(model_dict)
                    print('method= {} training hit_rate= {:.4f}'\
                              .format(method, hit_rate))

        for model in models_over_threshold:

            clf = model["model"]

            y_pred = clf.predict(X_validation)

            hit_rate = (sum(y_pred == y_validation))/len(y_pred)

            if hit_rate > highest_validation_model['hit_rate']:
                highest_validation_model['hit_rate'] = hit_rate
                highest_validation_model['picke_model'] = model;

            print('method = {0} validation hit_rate= {1:.4f}'.format(model['method'], hit_rate))

    if highest_validation_model['hit_rate'] > 0:
        print("Highest_validation_model's hit rate = {0:.2f}, method = {1}"\
            .format(highest_validation_model['hit_rate'], highest_validation_model['picke_model']['method']))
        #------ backtest 에 사용할 최종 model 저장
        fname_out = '{}-{}-{}-{}_model_for_backtest.pickle'.format(highest_validation_model['picke_model']['method'],\
                                                str(datetime.now().date()), lag, wink)
        with open(output_path + fname_out, 'wb') as f:
            pickle.dump(highest_validation_model['picke_model'], f)
    
        #------- save all results -------------
        output = pd.DataFrame(output,columns=cols)
        fname = '{}-{}-{}.csv'.format(str(datetime.now().date()), lags, win_K)
        output.to_csv(output_path + fname)

    else:
        print("No model passed over threshold = ", threshold)
        