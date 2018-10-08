import pandas as pd
import os
import pymysql.cursors
import sys
sys.path.append('../lib/')

from dbConnect import *

single_financial_file       = "\F_SCORE_single_fs_2016_4Q.csv"
consolidated_financial_file = "\F_SCORE_consolidated_fs_2016_4Q.csv"

path = os.getcwd()

try:
    sql = "ALTER TABLE stockcode ADD fscore SMALLINT NOT NULL AFTER smarket"
    cursor.execute(sql)
except:
    print("fscore not added")

def f_score_update(file):
    df = pd.read_csv(path + file,  encoding='CP949')

    f_score = df[['Code', 'fscore']]

    list = f_score.values

    for code, fscore in list:
        code = code.strip("A")
        try:
            sql = "UPDATE stockcode SET fscore = {} WHERE code = '{}'".format(fscore, code)
            cursor.execute(sql)
        except:
            print("Update failed: {}, {}".format(code, fscore))

    con.commit()

if __name__ == '__main__':
    f_score_update(single_financial_file)
    f_score_update(consolidated_financial_file)
