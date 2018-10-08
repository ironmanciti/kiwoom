@echo off
set _start=5930
set _finish=5930
set _step=10000
set /a _end = _start

:loop

if %_end% LEQ %_finish% (
  echo start = %_start% end= %_end% time= %TIME% >> logfile.txt
  python dailyCandleBatch.py "10081" %_start% %_end% "0" "20180931" "1"
  timeout /t 3
  set /a _start+=_step
  set /a _end=_start+_step
  goto :loop
)

goto :eof


("Arguments should be 1 : "10081"(opt10081 주식일봉차트 요청), 2: start_code, 3: end_code, 4: market_code ")
("         start_code / end_code / market_code /end_date/kospi200 should be given."
			     market CODE - 0: KOSPI, 3: ELW, 10: KOSDAQ, 8:ETF")
                                              end_date = "20180228" 기준일자, "1"-kospi200 only "0" 모든 종목
KOPI200 종목이면서 fscore > 7 이상 종목만 처리는 start, end 을 201777 로 SETTING : set _start=201777, set _end=201777
