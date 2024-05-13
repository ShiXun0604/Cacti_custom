import logging, datetime

def set_logger_filepath(logger, log_filepath):
    
    # remove all handlers in logger
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # set logger level
    logger.setLevel(logging.DEBUG)

    # set logger file name
    file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
    logger.addHandler(file_handler)

    # set logger format
    formatter = logging.Formatter('[%(asctime)s %(levelname)-8s] %(message)s')
    file_handler.setFormatter(formatter)




class Logger():
    def __init__(self, path, log_name) -> None:
        self.path = path
        self.log_name = log_name

    
    def set_logger_filepath(self, logger):
        current_datetime = datetime.datetime.now()
        log_filepath = '{}\{}_{}.txt'.format(self.path, self.log_name, current_datetime.strftime("%Y-%m-%d"))

        # set logger level
        logger.setLevel(logging.DEBUG)

        # set logger file name
        file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        logger.addHandler(file_handler)

        # set logger format
        formatter = logging.Formatter('[%(asctime)s %(levelname)-8s] %(message)s')
        file_handler.setFormatter(formatter)
    

    def debug(self, msg):
        # Set log file path
        logger = logging.getLogger()
        self.set_logger_filepath(logger)
        
        logger.debug(msg)

        del logger

def print_dict(dict):
	for key in dict.keys():
		print('{}\t{}'.format(key, dict[key]))