#----vanila mysql connect --------------------------------
import pymysql.cursors
con = pymysql.connect(host='localhost',user='yjoh',password='1234',db='stockdb',charset='utf8mb4')
cursor = con.cursor()

#----- pandas + mysql
from sqlalchemy import create_engine
engine = create_engine("mysql+pymysql://yjoh:1234@localhost/stockdb?charset=utf8",convert_unicode=True)
conn = engine.connect()
transaction = conn.begin()
#-----------------------------------------------
