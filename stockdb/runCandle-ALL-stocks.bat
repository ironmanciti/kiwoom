@echo off
set _start=000000
set _finish=900000
set _step=1000
set /a _end = _start + _step

:loop

if %_end% LEQ %_finish% (
  echo start = %_start% end= %_end% time= %TIME% >> logfile.txt
  python dailyCandleBatch.py "10081" %_start% %_end% "0" "20180228"
  timeout /t 3
  set /a _start+=_step
  set /a _end=_start+_step
  goto :loop
)

goto :eof


("Arguments should be 1 : 20006 or 10081, 2: start_code, 3: end_code, 4: market_code ")
("          in case of 20006, start_code=000000, end_code=999999, market_code=0, end_date=999999")
("          in case of 10081, start_code / end_code / market_code /end_date should be given.")
("                                            market CODE - 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF")
                                              end_date = "20180228" 기준일자
