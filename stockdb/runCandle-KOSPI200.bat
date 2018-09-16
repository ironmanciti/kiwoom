@echo off
set _start=201777
set _end=201777

echo start = %_start% end= %_end% time= %TIME% >> logfile.txt
python dailyCandleBatch.py "10081" %_start% %_end% "0" "20180228"

goto :eof

KOPI200 종목이면서 fscore > 7 이상 종목만 처리는 start, end 을 201777 로 SETTING
("Arguments should be 1 : 20006 or 10081, 2: start_code, 3: end_code, 4: market_code ")
("          in case of 20006, start_code=000000, end_code=999999, market_code=0, end_date=999999")
("          in case of 10081, start_code / end_code / market_code /end_date should be given.")
("                                            market CODE - 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF")
                                              end_date = "20180228" 기준일자
