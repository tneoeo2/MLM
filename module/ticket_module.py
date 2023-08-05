from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TicketModule(driver): 
    '''
        driver : 해당하는 드라이버 객체를 받는다
    '''
    def __init__(self):
        self.driver = driver
        
    
    def login_go(self, url, id, pwd): #로그인 함수
        '''
            url : 로그인할 사이트 주소
            id : 사용자 아이디
            pwd : 사용자 비밀번호
        '''
        self.driver.get(self.url)
        self.driver.switch_to.frame(self.driver.find_element_by_tag_name('iframe'))
        self.driver.find_element_by_name('userId').send_keys() #입력받은 id값 전달
        self.driver.find_element_by_id('userPwd').send_keys() #입력받은 pwd값 전달
        self.driver.find_element_by_id('btn_login').click() #로그인 버튼 클릭 이벤트
    
    def link_go(self, url):  #기본 : 미사용
        '''
        직링함수
        url : 직링용 url
        '''
        self.driver.get(url)
        
        
        
    def date_select(self, date:list):
        '''
        날짜 선택 함수
        date : 날짜를 담은 리스트 객체[월, 일]
        '''
        print("date_select 작동 확인!!")
        
        try:
            pop_up = self.driver.find_element_by_class_name("closeBtn")
            if pop_up is not None:
                print("popup닫기")
                pop_up.click()
        except Exception as e:
            print("ERROR : 팝업 없음", e)
            
        while (True):
            try: 
                self.driver.switch_to.default_content()
                # print("frame 교체 시도!")
                self.driver.switch_to.frame(self.driver.find_element_by_id('ifrmBookStep'))
                if int(date[0]) == 0:   #입력한 월 가져오기
                    pass
                elif int(date[0])  >= 1:  #입력한 월이 이번달이 아닌 경우
                    for i in range(1, int(date[0]) + 1):
                            self.driver.find_element_by_xpath("/html/body/div/div[1]/div[1]/div/span[3]").click()
                try:
                    # print(self.date_entry.get(), "날짜를 불러라")
                    self.driver.find_element_by_link_text(
                            date[1]).click()   
                    break
                except NoSuchElementException:    #찾는 요소 없을 경우 직링함수 재실행
                    self.link_go()
                    break
            except NoSuchElementException: 
                self.link_go()
                break
        self.wait.until(EC.element_to_be_clickable(     
            (By.XPATH, '/html/body/div/div[3]/div[1]/div/span/ul/li[' + self.round_entry.get() + ']/a'))).click()  #회차 클릭
        self.driver.switch_to.default_content()
        self.driver.find_element_by_id('LargeNextBtnImage').click()
        self.seat_select()     #*좌석 선택
    

def seat_select(self):
    '''
     좌석 선택함수
     
    '''
    self.driver.switch_to.default_content()   #!  상위로 이동
    self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
    self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail"))
    self.wait.until(EC.presence_of_element_located(    #원하는 요소가 뜰때까지 대기
        (By.CSS_SELECTOR, 'img[src="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/1_90.gif"]')))   #보라색 이미지 css 경로
    seats = self.driver.find_elements_by_css_selector(
        'img[src="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/1_90.gif"]')
    print("남은 좌석 수:", len(seats))   #남아있는 좌석 수
    
    """ 무조건 앞열 기준 잡기시작, 
    """
    
    if int(self.seat_entry.get()) > len(seats):   # 잡을 좌석 수 > 남은 좌석 수
        seat_count = len(seats)                 #남은 좌석만큼 가져오기
    else:
        seat_count = int(self.seat_entry.get())             #입력한 좌석 수만큼 가져오기
    for i in range(0, seat_count):
        seats[i].click()     #시트 클릭
    print("좌석 선택 완료!")
    self.driver.switch_to.default_content()
    self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))   #이전 프레임으로 돌아가기
    self.driver.find_element_by_id("NextStepImage").click()
    self.payment()         #*결제

def payment(self):
    '''
    결제 함수
    '''
    def bank():  #무통장
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Payment_22004"]/td/input'))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BankCode"]/option[7]'))).click()
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkAll"]'))).click()
        self.driver.switch_to.default_content()
        # self.driver.find_element_by_xpath('//*[@id="LargeNextBtnImage"]').click()    #?실결제는 주석처리
        
    def kakao(): #카카오
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Payment_22084"]/td/input'))).click()
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkAll"]'))).click()
        self.driver.switch_to.default_content()


    def task():
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
        self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="ifrmBookStep"]'))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="YYMMDD"]'))).send_keys(self.birth_entry.get())    #생년월일 입력
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath('//*[@id="SmallNextBtnImage"]').click()
        bank2 = self.bank_var.get()
        kakao2 = self.kakao_var.get()
        if bank2 == 1:
            bank()
        elif kakao2 == 1:
            kakao()