# kiwoom 에서 시장 종목 LIST 를 가져와 stockcode table 에 update 한다
import pandas as pd
import sqlalchemy
from bs4 import BeautifulSoup
import requests
import re
import sys

sys.path.append('../lib/')
from kiwoomMain import *
from dbConnect import *

app = QApplication(sys.argv)
markets = ['0', '3', '8', '10']   # 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF
kiwoom = Kiwoom()
kiwoom.comm_connect()

code_list = {}

for smarket in markets:
    list = kiwoom.get_code_list_by_market(smarket)
    code_list[smarket] = list

codeDict = {'code': [], 'code_name': [], 'smarket': []}

for smarket, list in code_list.items():
    for code in list:
        code_name = kiwoom.get_master_code_name(code)
        codeDict['code'].append(code)
        codeDict['code_name'].append(code_name)
        codeDict['smarket'].append(smarket)

df = pd.DataFrame(codeDict, columns=['code','code_name','smarket'])
df.to_sql('stockcode', conn, if_exists='replace', index=False,
             dtype={'code':  sqlalchemy.types.CHAR(6),
                    'code_name': sqlalchemy.types.VARCHAR(length=40),
                    'smarket': sqlalchemy.types.VARCHAR(length=40)})

transaction.commit()
conn.close()

print('code update complete')

BaseUrl = "http://finance.naver.com/sise/entryJongmok.nhn?&page="

data = []
for i in range(1,22):
    try:
        url = BaseUrl + str(i)
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")
        items = soup.find_all('td', attrs={'class': 'ctg'})

        for item in items:
            txt = item.a.get('href')
            k = re.search('[\d]+', txt)
            if k:
                code = k.group()
                name = item.text
                data.append((code, name))
    except:
        print("failed to get KOSPI200 stock codes from NAVER")

sql = "ALTER TABLE stockcode ADD kospi200 BOOLEAN NOT NULL DEFAULT False AFTER smarket"
cursor.execute(sql)

for code, name in data:
    try:
        sql = "UPDATE stockcode SET kospi200 = {} WHERE code = '{}'".format('TRUE',code)
        cursor.execute(sql)
    except:
        e = sys.exc_info()[0]
        print(e)

con.commit()
con.close()
print("kospi200 update complete")
