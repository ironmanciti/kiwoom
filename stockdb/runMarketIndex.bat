@echo off
set _start=0
set _end=999999

python dailyCandleBatch.py "20006" %_start% %_end% "xxx" "20180901" "0"

goto :eof

("Arguments should be "20006" (opt20006 업종일봉조회), 2: start_code, 3: end_code, 4: market_code ")
("          in case of 20006(업종일봉조회), start_code=000000, end_code=999999, market_code=xxx(dummy), end_date=999999", kospi="0"(dummy))

