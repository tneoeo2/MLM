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
TEST_MC = test_data['TEST_MC']['오유']
CAPTCHA_URL = test_data['CAPTCHA_URL']

INTERPARK_LOGIN_URL = "https://ticket.interpark.com/Gate/TPLogin.asp"

logging = CustomLogger("INFO").get_logger()

#?웹드라이버 불러오기(크롬)
def get_driver():
    driver = 0  #불러오기 실패시 0 반환
    driver = check_driver.ChromeCheck(driver).get_driver()
    
    return driver


def get_ticket():
    #!크롬드라이버 
    chrome_driver = get_driver()
    logging.info("---드라이버 가져오기---")
    #!사이트 접속(인터파크)
    logging.info("---티켓팅 모듈 실행---")
    tm = TicketModule(chrome_driver)
    tm.login_go(INTERPARK_LOGIN_URL, TEST_ID, TEST_PW)
    #!공연선택
    tm.link_go(TEST_MC)
    #!날짜 선택 & 7회차 선택
    tm.date_select(['1', '13'], '1')
    # tm.date_select(['1', '3'], '1')
    #!캡차 유무 선택 
    tm.read_captcha(url = CAPTCHA_URL, opt = 1)
    #!좌석 선택
    seat_name = ["VIP","R"]
    tm.seat_select(1, seat_name=seat_name)
    #!할인권종 선택
    tm.discount(0)
    #!결제 선택 - 무통장(0) -> 카카오(1)
    tm.payment(0, birth=TEST_BIRTH)

test_time = '14:01:20'    #?타이머 테스트용 
#!타임스레드 실행
#?타이머 불러오기 (다른 스레드 생성하여 진행)
timer_instance = timer.SetTimer()
# timer_instance = timer.SetTimer(test_time)
time_thread = threading.Thread(target=timer_instance.run)
logging.info("타임스레드 실행")
time_thread.start()

time_thread.join()

ticketing_thread = threading.Thread(target=get_ticket)
ticketing_thread.start()
logging.info("티켓팅스레드 실행")
