import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib
font_path = "C:/Windows/Fonts/H2GTRM.TTF"                       #폰트 경로
font_name = font_manager.FontProperties(fname=font_path).get_name()  #폰트 이름 얻어오기
matplotlib.rc('font', family=font_name)                                  #font 지정
matplotlib.rcParams['axes.unicode_minus'] = False               #한글사용시 마이너스 사인 깨짐 방지
