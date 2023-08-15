import logging

'''
< LOG LEVELS >
DEBUG: 프로그램 작동에 대한 상세한 정보를 가지는 로그. 문제의 원인을 파악할 때에만 이용.
INFO: 프로그램 작동이 예상대로 진행되고 있는지 트래킹하기 위해 사용.
WARNING: 예상치 못한 일이나 추후 발생 가능한 문제를 표시하기 위함.
ERROR: 심각한 문제로 인해 프로그램이 의도한 기능을 수행하지 못하고 있는 상황을 표시.
CRITICAL: 더욱 심각한 문제로 인해 프로그램 실행 자체가 언제라도 중단될 수 있음을 표시.
'''



class CustomLogger:
    
    def __init__(self, level="WARNING"):
        '''
        level : 로그확인할 단계 선택 (DEBUG < INFO < WARNING < ERROR < CRITICAL)
        '''
        self.level = level
    
    def get_logger(self):
        # logger
        logger = logging.getLogger("log")
        
        # Check handler exists
        if len(logger.handlers) > 0:
            return logger # Logger already exists
        
        logger_level = getattr(logging, self.level.upper(), "INFO")
        
        if not isinstance(logger_level, int):
            raise ValueError(f"Invalid log level: {self.level}")
        
        logger.setLevel(logger_level)
        
        handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info("server start!")
        
        return logger