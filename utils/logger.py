from amiyabot.log import LoggerManager

class Logger:
    def __init__(self):
        self.logger = LoggerManager('Kidnapper')

    def info(self,message:str):
        self.logger.info(f'{message}')

log = Logger()