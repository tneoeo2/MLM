import time
import threading
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# import module.ticket_module as tm
import module.check_driver as check_driver
import module.timer as timer


#?타이머 불러오기 (다른 스레드 생성하여 진행)

#?웹드라이버 불러오기(크롬)
def get_driver():
    driver = 0  #불러오기 실패시 0 반환
    driver = check_driver.ChromeCheck(driver).get_driver()
    
    return driver

test_time = '16:41:50'    #?타이머 테스트용 
#타임스레드 실행
timer_instance = timer.SetTimer(test_time)
time_thread = threading.Thread(target=timer_instance.run)
time_thread.start()


# chrome_driver = get_driver()

