import os
import time
import threading
import requests
import datetime

default_url = "http://ticket.interpark.com"


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
    def __init__(self, end_time: str):
        self.end_time = end_time
        self.current_time = '00:00:00.000'

    def run(self):
        while True:
            time.sleep(0.5)
            self.current_time = worker()[11:]
            print("current_time: ", self.current_time)
            h = int(self.current_time[:2])
            m = int(self.current_time[3:5])
            s = int(self.current_time[6:8])
            msec = int(self.current_time[9:])
            print(h, m, s, msec)
    
            if m == int(self.end_time[3:5]):  # 목표시간 도달하면
                if s - 1 == int(self.end_time[6:8]) and msec >= 500:
                    print("타이머 종료...", self.current_time)
                    return 1
                elif s == int(self.end_time[6:8]) :
                    print("타이머 종료...", self.current_time)
                    return 1

