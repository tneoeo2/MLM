import os
import requests
import json
import urllib.request
from requests_toolbelt import MultipartEncoder
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from module.custom_logger import CustomLogger

logging = CustomLogger("INFO").get_logger()

def close_pop(driver):
    try:
        pop_up = driver.find_element_by_class_name("closeBtn")
        if pop_up is not None:
            logging.info("popup닫기")
            pop_up.click()
    except Exception as e:
        logging.error("팝업 없음 : %s", e)


class TicketModule(): 
    '''
        driver : 해당하는 드라이버 객체를 받는다
    '''
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 5)
        
    
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
    
    def link_go(self, mc_code):  #티켓예매페이지로 이동
        '''
        mc_code: 예매할 공연 번호
        '''
        book_url = "http://poticket.interpark.com/Book/BookSession.asp?GroupCode="
        self.driver.get(book_url+str(mc_code))
        
        
        
    def date_select(self, date:list, times):
        '''
        날짜 선택 함수
        date : 날짜를 담은 리스트 객체[월, 일]
        times : 회차정보 (1부터 센다)
        '''
        logging.info("date_select 작동 확인")
        
        close_pop(self.driver)
            
        while (True):
            try: 
                self.driver.switch_to.default_content()
                # print("frame 교체 시도!")
                self.driver.switch_to.frame(self.driver.find_element_by_id('ifrmBookStep'))
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
                    self.link_go()
                    break
            except NoSuchElementException: 
                self.link_go()
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
        if opt == 1:
            logging.info("캡차 인식 실행")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
            img_captcha = self.wait.until(EC.presence_of_element_located((By.ID, 'imgCaptcha')))
            src = img_captcha.get_attribute('src')
            img_path = './img_captcha.png'
            urllib.request.urlretrieve(src, img_path)
            
            # 이미지 파일 서버로 전송
            headers = { 
            'accept': 'application/json',
            }
            files = {'file': (os.path.basename(img_path), open(img_path, 'rb'), 'image/png')}
            response = requests.post(url, headers=headers, files=files)
            json_response = json.loads(response.text)
            text_captcha = json_response['preds'][0]
            
            print(f'Response status code: {response.status_code}')
            print(f'Response content: {response.content.decode("utf-8")}')
        
            logging.info('캡차 결과 확인 : {}'.format(text_captcha))
            self.driver.find_element_by_xpath("//*[@id='divRecaptcha']/div[1]/div[3]/span").click()
            self.driver.find_element_by_id("txtCaptcha").send_keys(text_captcha)
            self.driver.find_element_by_id("txtCaptcha").send_keys(Keys.ENTER)
            #!캡차 인식 실패시 재시도 추가
                
        else:
            logging.info("캡차 인식 미사용")
    
    
        
        
    def seat_select(self, t_seat=1):
        '''
        좌석 선택함수
        t_seat : 선택할 좌석 수
        birth : 생일정보
        '''
        self.t_seat = t_seat
        self.driver.switch_to.default_content()   #!  상위로 이동
        self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
        self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail"))
        try:
            logging.info("보라색 좌석 시도")
            self.wait.until(EC.presence_of_element_located(    #원하는 요소가 뜰때까지 대기
                (By.CSS_SELECTOR, 'img[src="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/1_90.gif"]')))   #보라색 이미지 css 경로
            seats = self.driver.find_elements_by_css_selector(
                'img[src="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/1_90.gif"]')
        except Exception:
            logging.info("초록색 좌석 시도")
            self.wait.until(EC.presence_of_element_located(    #원하는 요소가 뜰때까지 대기
                (By.CLASS_NAME, 'stySeat')))   #초록 이미지 css 경로
            seats = self.driver.find_elements_by_class_name(
                'stySeat')
            
        logging.info("남은 좌석 수: {}".format(len(seats)))   #남아있는 좌석 수
        
        """ 무조건 앞열 기준 잡기시작, 
        """
        self.seat_count = 0 #실제 예매할 좌석의 수
        if self.t_seat > len(seats):   # 잡을 좌석 수 > 남은 좌석 수
            seat_count = len(seats)                 #남은 좌석만큼 가져오기
        else:
            seat_count = self.t_seat             #입력한 좌석 수만큼 가져오기
        for i in range(0, seat_count):
            seats[i].click()     #시트 클릭
        logging.info("좌석 선택 완료!")
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))   #이전 프레임으로 돌아가기
        self.driver.find_element_by_id("NextStepImage").click()




    ##? 가격할인권종 선택
    def discount(self, opt=0):
        logging.info("---권종선택 수행---")
        #일반 
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
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
        close_pop(self.driver)            

            
        
        
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
            self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
            logging.info("생일 입력 확인 : {}".format(self.birth))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="YYMMDD"]'))).send_keys(birth)    #생년월일 입력
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