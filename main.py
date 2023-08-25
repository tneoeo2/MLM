import time
import json
import threading
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from module.ticket_module import TicketModule
import module.check_driver as check_driver
import module.timer as timer
from module.custom_logger import CustomLogger

#추후 외부파일로 뺄것
test_data  = ''
# "CAPTCHA_URL" : "http://127.0.0.1:8000/read_captcha"
# "CAPTCHA_URL" : "http://port-0-cap-api-ac2nlljg1a0u.sel3.cloudtype.app/read_captcha"
with open('test.json', encoding='UTF8') as f:
    test_data = json.load(f)
    
TEST_ID = test_data['TEST_USER']['ID']
TEST_PW = test_data['TEST_USER']['PW']
TEST_BIRTH = test_data['TEST_USER']['BIRTH']

# TEST_ID = test_data['SOOIN']['ID']
# TEST_PW = test_data['SOOIN']['PW']
# TEST_BIRTH = test_data['SOOIN']['BIRTH']


# TEST_MC = test_data['TEST_MC']['더데빌']
TEST_MC = test_data['TEST_MC']['블메포']
CAPTCHA_URL = test_data['CAPTCHA_URL']

INTERPARK_LOGIN_URL = "https://ticket.interpark.com/Gate/TPLogin.asp"

logging = CustomLogger("INFO").get_logger()



#?웹드라이버 불러오기(크롬)
def get_driver():
    driver = 0  #불러오기 실패시 0 반환
    driver = check_driver.ChromeCheck(driver).get_driver()
    
    return driver



class TicketThread():
    def __init__(self, t_date:list, time=None, account:list=[TEST_ID, TEST_PW], t_time:int = 1, is_cap:int = 0, seat_cnt:int = 1, payment:int = 0):
        self.start_time = time
        self.account = account
        self.t_date = t_date
        self.t_time = t_time
        self.is_cap = is_cap
        self.seat_cnt = seat_cnt
        self.payment = payment
        
    def start_driver(self):
        logging.info("---드라이버 가져오기---")
        #!크롬드라이버 
        self.driver = get_driver()
        #!사이트 접속(인터파크)
        logging.info("---티켓팅 모듈 실행---")
        self.tm = TicketModule(self.driver)
        self.tm.login_go(INTERPARK_LOGIN_URL, self.account[0], self.account[1])
    
    def get_ticket(self):
        logging.info('---공연선택 시작---')
        #!공연선택
        self.tm.common_link_go(TEST_MC)
        #!날짜 선택[현재월+n,n일, n회차] & 회차 선택
        self.tm.common_date_select(self.t_date, self.t_time)
        #!캡차 유무 선택 
        self.tm.read_captcha(url = CAPTCHA_URL, opt = 0)
        #!좌석 선택(좌석수, [좌석이름, 구역] 입력)
        # seat_name = [["VIP", "B"], ["VIP", "C"], ["VIP", "A"], ["R", "B"], ["R", "C"], ["R", "A"]]
        seat_name = [["VIP"], ["R"], ["1층"]]
        self.tm.seat_select(1, seat_name=seat_name)
        #!할인권종 선택
        self.tm.discount(0)
        #!결제 선택 - 무통장(0) -> 카카오(1)
        self.tm.payment(0, birth=TEST_BIRTH)

    def run(self):
        self.start_driver()
        self.timer_instance = timer.SetTimer(self.start_time)
        time_thread = threading.Thread(target=self.timer_instance.run)
        logging.info("타임스레드 실행")
        time_thread.start()
        time_thread.join() #타이머 끝나면 티켓팅 시작
        self.get_ticket()
        
# test_time = '14:00:00'    #?타이머 테스트용 
test_time = '13:00:00'    #?타이머 테스트용 
# test_time = '00:22:00'    #?타이머 테스트용

#! 시작 전, 필요 정보 입력 !
account = [TEST_ID, TEST_PW] #로그인 정보(ID, PW)
t_date = [10, 5] #회차정보[[월, 일]
t_time = 1   # 회차
is_cap = 0   #캡차유무 설정 (0: 미사용, 1: 사용)
seat_cnt = 1 #좌석수
payment = 0  #결제 방법 선택(무통장:0, 카카오:1)
start_time = '14:00:00'    #?타이머 테스트용 


 
#!타임스레드 실행
#?타이머 불러오기 (다른 스레드 생성하여 진행)
ticketing_thread = threading.Thread(target=TicketThread(
    # start_time=None, 
    account=account, 
    t_date=t_date,
    t_time=t_time, 
    is_cap=is_cap,
    seat_cnt=seat_cnt,
    payment=payment
    ).run)
# ticketing_thread = threading.Thread(target=TicketThread(test_time).run)
ticketing_thread.start()
logging.info("티켓팅스레드 실행")
