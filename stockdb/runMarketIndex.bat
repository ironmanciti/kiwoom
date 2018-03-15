@echo off
set _start=0
set _end=999999

python dailyCandleBatch.py "20006" %_start% %_end% "xxx" "20180228"

goto :eof

("Arguments should be 1 : 20006 or 10081, 2: start_code, 3: end_code, 4: market_code ")
("          in case of 20006, start_code=000000, end_code=999999, market_code=0, end_date=999999")
("          in case of 10081, start_code / end_code / market_code /end_date should be given.")
