import os
import time
import threading
import requests
import datetime
from module.custom_logger import CustomLogger

default_url = "http://ticket.interpark.com"

logging = CustomLogger("INFO").get_logger()

def worker(url=default_url):
    '''
    url : 서버주소(default = 공원)
    '''
    
    response = requests.get(url)
    server_time = response.headers['date']

    dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    dt_formatted = dt.isoformat(timespec='milliseconds')    

    return dt_formatted
# print(worker())

class SetTimer:
    def __init__(self, end_time: str = None):
        if end_time is None:
            self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
            self.end_time = self.end_time.strftime("%H:%M:%S:%f")[:-3]
            logging.info("목표시간 : {}".format(self.end_time))
        else:
            self.end_time = end_time
            logging.info("목표시간 : {}".format(self.end_time))
        self.current_time = '00:00:00.000' #해당 서버 현재시간

    def run(self):
        while True:
            time.sleep(0.3)
            self.current_time = worker()[11:]
            # logging.info("current_time: %s", self.current_time)
            h = int(self.current_time[:2])
            m = int(self.current_time[3:5])
            s = int(self.current_time[6:8])
            msec = int(self.current_time[9:])
            formatted_time = f"{h:02}:{m:02}:{s:02}:{msec:03}"
            logging.info(formatted_time)
    
            if m == int(self.end_time[3:5]):  # 목표시간 도달하면
                if s - 1 == int(self.end_time[6:8]) and msec >= 700 :
                    logging.info(f"타이머 종료... {self.current_time}")
                    return 1
                elif s == int(self.end_time[6:8]) :
                    logging.info(f"타이머 종료... {self.current_time}")
                    return 1

