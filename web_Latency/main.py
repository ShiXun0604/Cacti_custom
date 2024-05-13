import datetime, sys, threading
from lib.log import *
from lib.MySQL_query import *
from lib.crawler import *
from lib.queue_lib import *


CONFIG_FILE_PATH = 'C:\cacti_expertos\WebLatency\WebLatency_config.xml'
with open(CONFIG_FILE_PATH, 'rb') as f:
    config = ET.fromstring(f.read().decode('utf-8'))

    # Load Mysql settings
    sql_setting = config.find('MysqlSetting')
    MYSQL_SETTING = {
        "host":sql_setting.find('host').text,
        "user":sql_setting.find('user').text, 
        "password":sql_setting.find('pwd').text,
        "database":sql_setting.find('database').text,
    }
    TABLE_NAME = sql_setting.find('table').text
    TABLE_PRIMARY_KEY = sql_setting.find('primaryKey').text

    # Create taget list
    TARGET_URL = {}
    for ele in config.find('targetList'):
        url = ele.find('url').text
        key_word = ele.find('keyWord').text
        timeout_setting = int(ele.find('timeoutSetting').text)
        TARGET_URL[url] = {
            'keyWord' : key_word,
            'timeoutSetting' : timeout_setting,
        }
    
    # Load monitor settings
    monitor_setting = config.find('monitorConfig')
    LOG_PATH = monitor_setting.find('logPath').text

    
    # Set log file path
    logger = logging.getLogger()
    current_datetime = datetime.datetime.now()
    log_filepath = '{}\{}_{}.txt'.format(LOG_PATH, TABLE_NAME, current_datetime.strftime("%Y-%m-%d"))
    set_logger_filepath(logger, log_filepath)
    logger.info('Program started.')

# checking mysql setting
try:
    MySQL_connection_testing(MYSQL_SETTING, detail=False)
    logger.debug('MySQL login test successful.')
except:
    logger.exception('MySQL login attempt failed.\n')
    logger.critical('Program stopped.')
    sys.exit()

# database reindexing
try:
    data_adjust = adjust_database(MYSQL_SETTING, TABLE_NAME, TABLE_PRIMARY_KEY, TARGET_URL.keys())

    # update static value
    with mysql.connector.connect(**MYSQL_SETTING) as connector:
        cursor = connector.cursor()
        for url in TARGET_URL.keys():
            # SQL command
            SQL_command = """
                UPDATE {} 
                SET keyword = '{}',  timeout = {}
                WHERE {} = '{}';
            """.format(TABLE_NAME, TARGET_URL[url]['keyWord'], TARGET_URL[url]['timeoutSetting'], TABLE_PRIMARY_KEY, url)
            cursor.execute(SQL_command)
        connector.commit()
        cursor.close()

    if data_adjust:
        logger.debug('Mysql adjusted data:\n{}'.format(data_adjust))
        logger.debug('Mysql data reindex success.')
except:
    logger.exception('Error occur while database reindexing.\n')
    logger.critical('Program stopped.')
    sys.exit()

# monit task start
try:
    thread_pool = []
    for url in TARGET_URL.keys():
        thread_pool.append(threading.Thread(target=Monit, args=[TARGET_URL[url]['keyWord'], url, TARGET_URL[url]['timeoutSetting']]))
    for i in thread_pool:
        # All threads wiil end in 10 seconds
        i.start()  
    for i in thread_pool:
        i.join()
    # log_append(log_text='Monit tasks done.')
except:
    logger.exception('Error occur while doing monit tasks.\n')
    #log_append(type='WARNING', log_text='Error occur while doing monit tasks.\n' + str(e))

# write monit data to MySQL
try:
    # update into database
    with mysql.connector.connect(**MYSQL_SETTING) as connector:
        cursor = connector.cursor()
        logger.debug('MySQL login successful.')
        for url in TARGET_URL.keys():
            # SQL command
            SQL_command = "UPDATE {} SET latency = {} WHERE {} = '{}';".format(TABLE_NAME, Latency[url], TABLE_PRIMARY_KEY, url)
            cursor.execute(SQL_command)
            
        connector.commit()
        cursor.close()
    logger.debug('Mysql data update success. Updated data count:{}'.format(len(TARGET_URL.keys())))
except Exception as e:
    logger.warning('Error occur while update data to MySQL.\n'+str(e))