import logging



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


def print_dict(dict):
	for key in dict.keys():
		print('{}\t{}'.format(key, dict[key]))