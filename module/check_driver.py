import chromedriver_autoinstaller
from selenium import webdriver

class ChromeCheck():
    
    def __init__(self, driver):
        self.driver = driver
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인
        print("check")
        try:
            self.opt = webdriver.ChromeOptions()
            self.opt.add_argument('window-size = 800, 600')
            self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=self.opt)   
        except:
            chromedriver_autoinstaller.install(True)
            self.opt = webdriver.ChromeOptions()
            self.opt.add_argument('window-size = 800, 600')
            self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=self.opt)   
            
        self.driver.implicitly_wait(10)

    def get_driver(self):   #? 최신버전 크롬드라이버 리턴
        # print("get_driver---- ", self.driver)
        return self.driver
    

