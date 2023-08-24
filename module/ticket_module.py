import os
import requests
import time
import json
import urllib.request
from requests_toolbelt import MultipartEncoderMonitor
from urllib3.exceptions import NewConnectionError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from module.custom_logger import CustomLogger

logging = CustomLogger("INFO").get_logger()

def close_default_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        logging.info("안내창 닫기")

def close_alert(driver):
    try:
        alert = driver.find_element_by_class_name("closeBtn")
        # alert = driver.switch_to.alert
        if alert is not None:
            logging.info("popup닫기")
            # alert.accept()
            alert.click()
    except Exception as e:
        logging.error("팝업 없음 : %s", e)
        
def common_close_alert(driver):
    try:
        alert = driver.find_element_by_class_name("popupCloseBtn")
        # alert = driver.switch_to.alert
        if alert is not None:
            logging.info("popup닫기")
            # alert.accept()
            alert.click()
    except Exception as e:
        logging.error("팝업 없음 : %s", e)

# 대기열 떳을 경우 기다리기
def waiting_order(driver):
    is_waiting = driver.find_element(By.CLASS_NAME, "ticketWaiting__order")
    while True:
        if is_waiting :
            waiting_num = driver.find_element(By.CLASS_NAME, "notranslate")
            time.sleep(3)
            logging.info(f"대기중...{waiting_num}")
            pass
        else:
            break
        
def scroll_to(driver, pos:list=[0, 0]):
    try:
        script = f"window.scrollTo({pos[0]}, {pos[1]});"
        driver.execute_script(script)

    except Exception as e:
        print("스크롤을 조정할 수 없거나 오류 발생:", e)           
        
def switch_window(driver, current_windows):
    '''
    current_windows : 기존 윈도우창 정보
    '''
    try:
        all_window_handles = driver.window_handles
        
        
        # 팝업 윈도우 핸들 찾기
        new_window_handle = None
        for window_handle in all_window_handles:
            if window_handle not in current_windows:
                new_window_handle = window_handle
                break
            
        if new_window_handle:
            # 팝업 윈도우로 전환s
            driver.switch_to.window(new_window_handle)
            logging.info("driver switched")
            return new_window_handle
    except:
        logging.error("Failed to switch")
    

class TicketModule(): 
    '''
        driver : 해당하는 드라이버 객체를 받는다
    '''
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 4)
        
    
    def login_go(self, url, id, pwd): #로그인 함수
        '''
            url : 로그인할 사이트 주소
            id : 사용자 아이디
            pwd : 사용자 비밀번호
        '''
        self.driver.get(url)
        self.driver.switch_to.frame(self.driver.find_element_by_tag_name('iframe'))
        self.driver.find_element_by_name('userId').send_keys(id) #입력받은 id값 전달
        self.driver.find_element_by_id('userPwd').send_keys(pwd) #입력받은 pwd값 전달
        self.driver.find_element_by_id('btn_login').click() #로그인 버튼 클릭 이벤트
    
    def common_link_go(self, mc_code, alert=False):
        ##! 사용 전 해당링크 접속시 뜨는 팝업 모두 '오늘 하루 보지 않기' 처리 후 사용
        self.mc_code = mc_code
        book_url = "https://tickets.interpark.com/goods/"
        try:
            self.driver.get(book_url+str(self.mc_code))
            if alert : 
                common_close_alert(self.driver)
        except Exception as e:
            logging.error(f"Exception e : {e}")
            
    def common_date_select(self, date:list, times):
        '''
        날짜 선택 함수
        date : 날짜를 담은 리스트 객체[월, 일]
        times : 회차정보 (1부터 센다)
        '''
        logging.info("common_date_select 작동 확인")
        common_close_alert(self.driver)
        # current = self.driver.find_element(By.CSS_SELECTOR, "li[data-view='month current']")
        # current_mon = current.text.split(".")[-1].strip() #현재 월 확인
        # logging.info(f"Current month: {current_mon}")
        while (True):
            try:
                if int(date[0]) == 0:   #입력한 월 가져오기
                        pass
                elif int(date[0]) >= 1:  #입력한 월이 이번달이 아닌 경우
                    for _ in range(int(date[0])):
                        scroll_to(self.driver, ['document.body.scrollWidth', 0])
                        self.driver.find_element(By.CSS_SELECTOR, "li[data-view='month next']").click()
                try:
                    # print(self.date_entry.get(), "날짜를 불러라")
                    date_picker = self.driver.find_element(By.CSS_SELECTOR, "ul[data-view='days']")
                    blank = len(date_picker.find_elements(By.CLASS_NAME, "muted"))
                    list_num = int(date[1])+blank
                    self.driver.find_element(By.XPATH, f'//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[{list_num}]').click()   
                    break
                except NoSuchElementException:    #찾는 요소 없을 경우 직링함수 재실행
                    self.common_link_go(self.mc_code, True)
                    break
            except NoSuchElementException: 
                self.common_link_go(self.mc_code, True)
                break
        self.driver.switch_to.default_content()
        scroll_to(self.driver, ['document.body.scrollWidth', 'document.body.scrollHeight'])   #스크롤 내리기
        times_loc = f'//a[contains(@data-text,"{times}")]'
        self.driver.find_element(By.XPATH, times_loc)
        current_windows = self.driver.window_handles
        self.driver.find_element_by_xpath('//*[@id="productSide"]/div/div[2]/a[1]').click()
        self.ticket_windows = switch_window(self.driver, current_windows)
        
     
    def link_go(self, mc_code, alert=False):  #티켓예매페이지로 이동
        '''
        mc_code: 예매할 공연 번호
        alert : 팝업 유무
        '''
        self.mc_code = mc_code
        try:
            book_url = "http://poticket.interpark.com/Book/BookSession.asp?GroupCode="
            self.driver.get(book_url+str(self.mc_code))
            if alert : 
                close_alert(self.driver)
        except :
            self.link_go(self.mc_code, alert=True)
        
        
        
    def date_select(self, date:list, times):
        '''
        날짜 선택 함수
        date : 날짜를 담은 리스트 객체[월, 일]
        times : 회차정보 (1부터 센다)
        '''
        logging.info("date_select 작동 확인")
        while (True):
            try: 
                self.driver.switch_window(self.ticket_windows)
                self.driver.switch_to.default_content()
                # print("frame 교체 시도!")
                t_ifrm = self.driver.find_element_by_id('ifrmBookStep')
                self.wait.until(EC.frame_to_be_available_and_switch_to_it(t_ifrm))
                # self.driver.switch_to.frame(self.driver.find_element_by_id('ifrmBookStep'))
                if int(date[0]) == 0:   #입력한 월 가져오기
                    pass
                elif int(date[0])  >= 1:  #입력한 월이 이번달이 아닌 경우
                    for i in range(1, int(date[0]) + 1):
                        self.driver.find_element_by_xpath("/html/body/div/div[1]/div[1]/div/span[3]/a/img").click()
                try:
                    # print(self.date_entry.get(), "날짜를 불러라")
                    self.driver.find_element_by_link_text(date[1]).click()   
                    break
                except NoSuchElementException:    #찾는 요소 없을 경우 직링함수 재실행
                    self.link_go(self.mc_code, True)
                    break
            except NoSuchElementException: 
                self.link_go(self.mc_code, True)
                break
        self.wait.until(EC.element_to_be_clickable(     
            (By.XPATH, '/html/body/div/div[3]/div[1]/div/span/ul/li[' + times + ']/a'))).click()  #회차 클릭
        self.driver.switch_to.default_content()
        self.driver.find_element_by_id('LargeNextBtn').click()
    
    #캡차인식
    def read_captcha(self, url, opt=0):
        '''
        url : 캡차 URL
        opt: 0(미사용), 1(사용)
        '''
        try:
            if opt == 1:
                logging.info("캡차 인식 실행")
                self.driver.switch_to.default_content()   #!  상위로 이동
                logging.info("캡차 인식 실행2")
                # self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_name("ifrmSeat")))
                logging.info(f'iframe 확인 1 : {self.driver.find_element(By.ID,"ifrmSeat")}')
                logging.info(f'iframe 확인 2 : {self.driver.find_element_by_name("ifrmSeat")}')
                self.driver.switch_to.frame(self.driver.find_element(By.ID, "ifrmSeat"))
                logging.info("캡차 인식 실행3")
                img_captcha = self.wait.until(EC.presence_of_element_located((By.ID, 'imgCaptcha')))
                src = img_captcha.get_attribute('src')
                img_path = './img_captcha.png'
                urllib.request.urlretrieve(src, img_path)
                
                # 이미지 파일 서버로 전송
                headers = { 
                'accept': 'application/json',
                }
                files = {'file': (os.path.basename(img_path), open(img_path, 'rb'), 'image/png')}
                text_captcha = 0
                try:
                    response = requests.post(url, headers=headers, files=files)
                except NewConnectionError as e:
                    logging.error(f"캡차 서버 통신 오류---{e}")
                try:
                    json_response = json.loads(response.text)
                    text_captcha = json_response['preds'][0]
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decoding error: {e}")
                # print("response: " , response.text)
                print(f'Response status code: {response.status_code}')
                print(f'Response content: {response.content.decode("utf-8")}')
            
                logging.info('캡차 결과 확인 : {}'.format(text_captcha))
                self.driver.find_element_by_xpath("//*[@id='divRecaptcha']/div[1]/div[3]/span").click()
                self.driver.find_element_by_id("txtCaptcha").send_keys(text_captcha)
                self.driver.find_element_by_id("txtCaptcha").send_keys(Keys.ENTER)
                #!캡차 인식 실패시 재시도 추가
                captcha_fail = self.driver.find_element(By.CLASS_NAME, 'validationTxt')
                border_color_default = "rgb(170, 170, 170)"
                border_color = captcha_fail.value_of_css_property('border-color')
                logging.info('border_color: %s', border_color)
                if border_color != border_color_default:
                    logging.info('Captcha 인식 실패')
                    self.read_captcha(url, opt)
            else:
                logging.info("캡차 인식 미사용")
        except Exception as e:
            logging.error(f"Error {e}--- 캡차인식을 재실행 합니다...")
            self.read_captcha(url, opt)
    
        
        
    def seat_select(self, t_seat=1, seat_name=None):
        '''
        좌석 선택함수
        t_seat : 선택할 좌석 수
        seat_name : 선택할 좌석명 (ex. R석, VIP석 등)
        birth : 생일정보
        '''
        self.t_seat = t_seat
        self.driver.switch_to.default_content()   #!  상위로 이동
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_name("ifrmSeat")))
        # self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_name("ifrmSeatDetail")))
        # self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail"))
        
        seats = 0
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stySeat')))   #초록 이미지 css 경로
        try:
            if seat_name is not None : 
                for i in range(len(seat_name)):
                    logging.info("{} 좌석 선택 시도".format(seat_name[i][0]))
                    #! 기본
                    # xpath = f'//img[contains(@title,"{seat_name[i]}")]'
                    #? 리터럴
                    # xpath = f'//img[contains(@title,"{seat_name[i]}") and contains(@title,"1층") and contains(@title,"B")]'
                    css_selector = f'img[title*="{seat_name[i][0]}"][title*="{seat_name[i][1]}"]'
                    # self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))  #원하는 요소가 뜰때까지 대기'
                    seats.append(self.driver.find_elements_by_css_selector(css_selector))  #*선택자로 가져오기
                    # seats = self.driver.find_elements_by_xpath(xpath)   #*xpath로 탐색 
                    if len(seats) >= self.t_seat:
                        break
        except:
            logging.info("입력한 등급의 좌석이 남아있지 않습니다. --> 남은 좌석 중 랜덤 선택")
            seats = self.driver.find_elements_by_class_name('stySeat')
            
            
        logging.info("남은 좌석 수: {}".format(len(seats)))  
        
        if len(seats) == 0:
            logging.info("입력한 등급의 좌석이 남아있지 않습니다. --> 남은 좌석 중 랜덤 선택")
            seats = self.driver.find_elements_by_class_name('stySeat')
            #남아있는 좌석 수
        try:    
            self.seat_count = 0 #실제 예매할 좌석의 수
            if self.t_seat > len(seats):   # 잡을 좌석 수 > 남은 좌석 수
                self.seat_count = len(seats)                 #남은 좌석만큼 가져오기
            else:
                self.seat_count = self.t_seat             #입력한 좌석 수만큼 가져오기
            for i in range(0, self.seat_count):
                seats[i].click()     #시트 클릭
            logging.info("좌석 선택 완료!")
        except UnexpectedAlertPresentException as e:
            logging.error(f"ERROR: {e}")
            close_default_alert(self.driver)
            self.seat_select(t_seat, seat_name)
            
            
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))   #이전 프레임으로 돌아가기
        self.driver.find_element_by_id("NextStepImage").click()




    ##? 가격할인권종 선택
    def discount(self, opt=0):
        '''
        opt : 0(일반), 1(재관)
        '''
        logging.info("---권종선택 수행---")
        #일반 
        self.driver.switch_to.default_content()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element(By.XPATH,'//*[@id="ifrmBookStep"]')))
        # self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        if opt == 0:
            # pricegradename 값
            desired_pricegradename = "일반"
            # pricegradename 속성 값을 기반으로 요소 찾기
            xpath = f"//select[contains(@pricegradename,'{desired_pricegradename}')]"
            # matching_elements = self.driver.find_elements(By.XPATH, xpath)
            select_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            # Select 객체 생성
            select = Select(select_element)
            # 원하는 <option> 요소 선택
            select.select_by_value(str(self.seat_count))   
        #재관람
        elif opt == 1:
            # pricegradename 값
            desired_pricegradename = "재관람"
            # pricegradename 속성 값을 기반으로 요소 찾기
            xpath = f"//select[contains(@pricegradename,'{desired_pricegradename}')]"
            # matching_elements = self.driver.find_elements(By.XPATH, xpath)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            # matching_elements = self.driver.find_elements(By.XPATH, xpath)
            select_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            # Select 객체 생성
            select = Select(select_element)
            # 원하는 <option> 요소 선택
            select.select_by_value(str(self.seat_count))  
            
        self.driver.switch_to.default_content() 
        self.driver.find_element_by_id("SmallNextBtnImage").click()
        close_alert(self.driver)            

            
        
        
    def payment(self, pay_opt:int = 0, birth=None):
        '''
        결제 함수
        '''
        self.pay_opt = pay_opt
        self.birth = birth
        logging.info("---결제 수행---")
        
        def bank():  #무통장
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Payment_22004"]/td/input'))).click()
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BankCode"]/option[7]'))).click()
            self.driver.switch_to.default_content()
            self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkAll"]'))).click()
            self.driver.switch_to.default_content()
            ##! 실사용시 주석 해제 후 사용할 것!!!
            # self.driver.find_element_by_xpath('//*[@id="LargeNextBtnImage"]').click()    #?실결제는 주석처리
            
        def kakao(): #카카오
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Payment_22084"]/td/input'))).click()
            self.driver.switch_to.default_content()
            self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkAll"]'))).click()
            self.driver.switch_to.default_content()
            self.driver.find_element_by_xpath('//*[@id="LargeNextBtnImage"]').click()
            #결제하기 동의
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="formConfirm"]/div[1]/div/div[1]/div[2]/ul/li[1]/label'))).click()
            self.driver.find_element_by_xpath('//*[@id="LargeNextBtnImage"]').click()

        def task():
            self.driver.switch_to.default_content()
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]')))
            #self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            logging.info("생일 입력 확인 : {}".format(self.birth))
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#YYMMDD'))).send_keys(birth)    #생년월일 입력
            # self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
            self.driver.switch_to.default_content()
            self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            if self.pay_opt == 0:
                try:
                    bank()
                except TimeoutException:
                    logging.error("---무통장결제가 불가능한 대상입니다---")
                    kakao()
            elif self.pay_opt == 1:
                kakao()
            '''bank2 = 1
            kakao2 = self.kakao_var.get()
            if bank2 == 1:
                bank()
            elif kakao2 == 1:
                kakao()'''
        task()