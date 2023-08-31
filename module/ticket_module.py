import os
import requests
import time
import json
import urllib.request
from requests_toolbelt import MultipartEncoderMonitor
from urllib3.exceptions import NewConnectionError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
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
            return True
    except Exception as e:
        logging.error("팝업 없음 : %s", e)
        
def common_close_alert(driver):
    try:
        alert = driver.find_element_by_class_name("popupCheckLabel")
        # alert = driver.switch_to.alert
        if alert is not None:
            logging.info("popup닫기")
            # alert.accept()
            alert.click()
    except Exception as e:
        logging.error("팝업 없음 : %s", e)

#네이게이션바에서 특정 선택창클릭
def go_navi(driver, opt=2):
    '''
    opt : 1(회차선택), 2(좌석선택), 3(가격, 할인선택), 4(배송/주문자할인)
    '''
    driver.switch_to.default_content()
    t_navi = f'//*[@id="divBookMain"]/div[2]/div[1]/ul/li[{opt}]'
    driver.find_element(By.XPATH, t_navi).click()
    
    
    
    
    
# 대기열 떳을 경우 기다리기
def waiting_order(driver):
    try:
        is_waiting =  WebDriverWait(driver, 4).until(EC.presence_of_element_located(By.CLASS_NAME, "ticketWaiting__order"))
        while True:
            if is_waiting :
                # WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CLASS_NAME, 'notranslate'))) 
                waiting_num = driver.find_element(By.CLASS_NAME, "notranslate")
                time.sleep(1)
                logging.info(f"대기중...{waiting_num.text}")   #span 클래스 : notranslate 값가져오기
                pass
            else:
                logging.info("대기열 없음..")
                break
    except Exception as e:
        logging.error(f'Error 대기 번호 존재하지않음 : {e}')
            
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
            self.common_link_go(mc_code, alert=True)
            logging.error(f"Exception e : {e}")
            
    def common_date_select(self, date:list, times):
        '''
        날짜 선택 함수
        date : 날짜를 담은 리스트 객체[월, 일]
        times : 회차정보 (1부터 센다)
        '''
        logging.info("common_date_select 작동 확인")
        try:
            self.driver.refresh()
        except Exception:
            logging.info("창 새로고침")
        try:# common_close_alert(self.driver)
            current = self.driver.find_element(By.CSS_SELECTOR, "li[data-view='month current']")
            current_mon = int(current.text.split(".")[-1].strip()) #현재 월 확인
            next = self.driver.find_element(By.CSS_SELECTOR, "li[data-view='month next']")
            t_mon = int(date[0])
            logging.info(f"Current month: {current_mon}")
        except Exception as e:
            self.common_date_select(date, times)
            return
        flg = True
        while (flg):
            try:
                logging.info(f"{date[0]}월 선택")
                if t_mon == current_mon:   #입력한 월 가져오기
                        pass
                elif t_mon != current_mon:  #입력한 월이 이번달이 아닌 경우
                    change = t_mon-current_mon
                    if change < 0 :  #예매월이 다음 달로 넘어가는 경우
                        t_mon += 12
                        change = t_mon-current_mon
                    else:
                        pass
                    scroll_to(self.driver, ['document.body.scrollWidth', 0])
                    for _ in range(change):
                        next.click()
                try:
                    logging.info(f"{date[1]}일 선택")
                    date_picker = self.driver.find_element(By.CSS_SELECTOR, "ul[data-view='days']")
                    dates = date_picker.find_elements(By.TAG_NAME, "li")
                    for d in dates:
                        if int(d.text) == date[1]:
                            d.click()   
                            if d.get_attribute("class") !="picked":
                                raise NoSuchElementException("선택할수 없는 날짜: 날짜 로딩 확인")
                            else:
                                flg = False
                            break
                except NoSuchElementException  as e:    #찾는 요소 없을 경우 직링함수 재실행
                    logging.error(f"날짜 선택 에러 1: {e}")
                    self.common_link_go(self.mc_code, True)
                    self.common_date_select(date, times)
                    return
            except NoSuchElementException as e: 
                logging.error(f"날짜 선택 에러 2: {e}")
                self.common_link_go(self.mc_code, True)
                self.common_date_select(date, times)
                return
            except ElementClickInterceptedException as e:
                logging.error(f"날짜 선택 에러 3: {e}")
                self.common_link_go(self.mc_code, True)
                self.common_date_select(date, times)
                return
        self.driver.switch_to.default_content()
        scroll_to(self.driver, ['document.body.scrollWidth', 'document.body.scrollHeight'])   #스크롤 내리기
        times_loc = f'//a[contains(@data-text,"{times}")]'
        self.driver.find_element(By.XPATH, times_loc)
        current_windows = self.driver.window_handles
        self.driver.find_element_by_xpath('//*[@id="productSide"]/div/div[2]/a[1]').click()
    
        try:
            time.sleep(0.5)
            self.ticket_windows = switch_window(self.driver, current_windows)
            try:
                '''
                # WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "ifrmSeat")))
                # logging.info("토핑 선예매 팝업")
                # self.ticket_windows = switch_window(self.driver, current_windows)
                WebDriverWait(self.driver, 0.5).until(EC.presence_of_element_located((By.ID, "Notice"))).click()
                window_handles = self.driver.window_handles
                self.driver.switch_to_window(window_handles[-1])
                self.driver.find_element_by_xpath('//*[@id="productSide"]/div/div[2]/a[1]').click()
                self.ticket_windows = switch_window(self.driver, current_windows)
                '''
                self.ticket_windows = switch_window(self.driver, current_windows)
                logging.info(f'예매창 전환 확인 : {self.driver.find_element(By.ID, "divBookMain")}')  #창 전환 확인용
            except Exception as e:
                while True:
                    logging.error(f"토핑 팝업 제거 필요: {e}")
                    time.sleep(0.5)
                    try:
                        self.driver.find_element(By.ID, "divBookMain")  #창 전환 확인용
                        break
                    except Exception:
                        continue
                        
                    
        except Exception as e:
            logging.error(f'좌석 예매창 가기 실패---{e}')
            # self.common_link_go(self.mc_code)
            self.common_date_select(date, times)
        # waiting_order(self.driver)
        
     
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
                # self.wait.until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_name("ifrmSeat")))
                # logging.info(f'iframe 확인 2 : {self.driver.find_element_by_name("ifrmSeat")}')
                try:
                    self.driver.switch_to.frame(self.driver.find_element(By.ID, "ifrmSeat"))
                except Exception as e:
                    close_alert(self.driver)
                    logging.error(f"캡차 이미지 없음 : {e}")
                    waiting_order(self.driver)
                    self.driver.switch_to.frame(self.driver.find_element(By.ID, "ifrmSeat"))
                # logging.info("캡차 인식 실행3")
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
            logging.error(f"캡차인식을 오류---Error : {e}")
            logging.info("수동 입력하세요.---")
            while True:
                time.sleep(1)
                div_element = self.driver.find_element_by_id("divRecaptcha")
                display_style = div_element.get_attribute("style")
                print("display style: " + display_style)
                if display_style != '':
                    logging.info("캡차 입력 완료")
                    break                    
            
    def coord_seat_select(self, seat_name:str=None): #좌표로 좌석가져오기
        '''
        좌석 선택함수
        t_seat : 선택할 좌석 수
        seat_name : 탐색할 좌석명 (default=None : 전체 탐색) 
        '''
        coord_seats = []   # 조건에 맞는 좌석 리스트
        try:
            #? 시간 체크
            start_time = time.time()

            css_selector = f'img[title*="{seat_name.strip()}"]'
            #해당 등급의 좌석만 가져옴            
            # img_elements = WebDriverWait(self.driver, 2).until(
                # EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            img_elements = self.driver.find_elements_by_css_selector(css_selector)
            if len(img_elements) == 0:   #없으면 바로 return
                return coord_seats
            
            for img in img_elements:
                style = img.get_attribute("style")
                left = None
                top = None
                
                # style 속성에서 left와 top 값 추출
                style_parts = style.split(";")
                style_left_top = []
                for part in style_parts:
                    if "left:" in part:
                        left = int(part.split(":")[1].strip()[:-2])  # "left:" 다음의 값
                        style_left_top.insert(0,left)
                    elif "top:" in part:
                        top = int(part.split(":")[1].strip()[:-2])  # "top:" 다음의 값
                        style_left_top.insert(1, top)
                        
                coord_seats.append([img, style_left_top])
                    
            coord_seats.sort(key=lambda x: (x[1][1], x[1][0]))   #top기준 오름차순정렬
                
                # if left is not None and top is not None:    #? 같은 값이 어떻게 처리..(ex. 200, 0 <-> 0, 200)
                #     left_top_sum = left + top
                #     if left_top_sum < min_left_top:
                #         min_left_top = left_top_sum
                #         min_img = img
                #     if left_top_sum > max_left_top:
                #         max_left_top = left_top_sum
                #         max_img = img
                        
            logging.info(f"좌표 계산 시간 체크 :  {time.time() - start_time}")
            # logging.info(f"가장 작은 left 값을 가진 img 태그: {min_img.get_attribute('outerHTML')}")
            
            # logging.info(f"가장 큰 left 값을 가진 img 태그: {max_img.get_attribute('outerHTML')}")
            
            return coord_seats    
        except Exception as e:
            logging.error(f"작업을 수행하는 동안 오류 발생: {e}")
            return coord_seats

        
        
    def seat_select(self, t_seat=1, seat_name:list=None):
        '''
        좌석 선택함수
        t_seat : 선택할 좌석 수
        seat_name : 선택할 좌석명 (ex. R석, VIP석 등)
        '''
        self.t_seat = t_seat
        self.seat_name = seat_name
        self.picked_seat = 0
        coord_seats = []  #남아있는 좌석 담을 리스트
        
        try:
            time.sleep(0.5)
            self.driver.switch_to_window(self.driver.window_handles[-1])
            self.driver.switch_to.default_content()   #!  상위로 이동
            self.wait.until(EC.presence_of_element_located((By.ID, "ifrmSeat")))
            self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
            self.wait.until(EC.presence_of_element_located((By.ID, "ifrmSeatDetail")))
            self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail")) #초록 이미지 css 경로
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stySeat')))   #초록 이미지 css 경로
        except Exception as e:
            logging.error(f'좌석 요소 탐색 실패 : {e}')
            logging.info(f'팝업창이 있다면 닫아주세요')
            time.sleep(2)
            logging.info(f'재시도')
            try:
                self.driver.switch_to.default_content()   #!  상위로 이동
                self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
                self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail")) #초록 이미지 css 경로
            except:
                logging.error("Failed to Retry")
                waiting_order(self.driver)
                self.seat_select(t_seat, seat_name)
                return
            
        
        # self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))
        # self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeatDetail"))
        
        seats = []
        try:
            if seat_name is not None : 
                for i in range(len(seat_name)):
                    logging.info("{} 좌석 선택 시도".format(seat_name[i]))
                    try:
                        coord_seats = self.coord_seat_select(seat_name[i])
                    except:
                        pass
                    if len(coord_seats) !=  0:
                        try:
                            for j in range(self.t_seat):
                                coord_seats[j][0].click() 
                                logging.info(f'{coord_seats[j][0]} -- 좌석 선택 완료')
                                self.picked_seat += 1 #선택 성공시 +1 
                        except:
                            logging.info(f"{seat_name[i]} : 해당 좌석 없음")
                    else: 
                        continue
                    # seats = self.driver.find_elements_by_xpath(xpath)   #*xpath로 탐색 
                    if self.picked_seat >= self.t_seat:
                        break
            else:
                logging.info("전체 좌석중 선택")
                seats = self.driver.find_elements_by_class_name('stySeat')
                logging.info("전체 남은 좌석 수: {}".format(len(seats)))
                
        except:
            logging.info("입력한 등급의 좌석이 남아있지 않습니다. --> 남은 좌석 중 랜덤 선택")
            seats = self.driver.find_elements_by_class_name('stySeat')
            logging.info("전체 남은 좌석 수: {}".format(len(seats)))
        
        try:
            for i in range(len(seats)):
                try:
                    if self.picked_seat < self.t_seat:
                        seats[i].click()
                        self.picked_seat += 1
                    if self.picked_seat >= self.t_seat:
                        logging.info("지정 영역 외랜덤 좌석 선택완료")
                        break     
                except Exception as e:
                    logging.error(f"중복 좌석 선택 에러 : {e}")
        except Exception as e:
            logging.error(f"좌석 선택 에러 : 남은 좌석없음 -- {e}")
        
        try:    
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element_by_name("ifrmSeat"))   #이전 프레임으로 돌아가기
            self.driver.find_element_by_id("NextStepImage").click()
            if close_default_alert(self.driver)  :
                logging.info("이선좌 오류")
                self.seat_select(t_seat, seat_name)
                
        except Exception as e:
            close_default_alert(self.driver)
            logging.error(f"좌석 선택에러 : {e} ")
            self.seat_select(t_seat, seat_name)
        
        



    ##? 가격할인권종 선택
    def discount(self, opt=0):
        '''
        opt : 0(일반), 1(재관)
        '''
        try:
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
                select.select_by_value(str(self.picked_seat))   
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
                select.select_by_value(str(self.picked_seat))  
                
            self.driver.switch_to.default_content() 
            self.driver.find_element_by_id("SmallNextBtnImage").click()
        except Exception as e:
            logging.error(f"권종 선택 중 오류 --- {e}")
            close_alert(self.driver)   
            self.seat_select(self.t_seat, self.seat_name)
            # go_navi(self.driver, opt=2)

            
        
        
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
            self.driver.find_element_by_xpath('//*[@id="La/geNextBtnImage"]').click()    #?실결제는 주석처리
            
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