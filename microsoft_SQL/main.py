from lib.msSQL import * 
from lib.MySQL_query import *
from lib.log import *

import xml.etree.ElementTree as ET
import threading, datetime, sys



# Static
TARGET_MSSQL_SETTING_LIST = {}
MONIT_INTERVAL = 10  # 偵測的秒數間隔,需要是300的因數
DATA_COUNT = 300 / MONIT_INTERVAL
WRITE_NIN = 4  # 寫入cacti database的時間
WRITE_NIN = (time.localtime().tm_min+1)%5  # 測試用

# 將config檔讀入
with open('C:\cacti_expertos\microsoftSQL\microsoftSQL_config.xml', 'rb') as f:
    # 讀進cacti mysql設定
    config = ET.fromstring(f.read().decode('utf-8'))
    sql_setting = config.find('MysqlSetting')
    MYSQL_SETTING = {
        "host":sql_setting.find('host').text,
        "user":sql_setting.find('user').text, 
        "password":sql_setting.find('pwd').text,
        "database":sql_setting.find('database').text,
    }
    TABLE_NAME = sql_setting.find('table').text
    TABLE_PRIMARY_KEY = sql_setting.find('primaryKey').text
    
    # Load monitor settings
    monitor_setting = config.find('monitorConfig')
    LOG_PATH = monitor_setting.find('logPath').text

    # 讀進待測microsoft SQL資料
    for ele in config.find('targetList'):
        svr_IP = ele.find('IP').text
        TARGET_MSSQL_SETTING_LIST[svr_IP] = {'server':svr_IP,
                                             'user' : ele.find('user').text,
                                             'password' : ele.find('pwd').text,}
    
    
# 準備資料表
IP = TARGET_MSSQL_SETTING_LIST.keys()  # IP列表
for ip in IP:
    Data[ip] = {}

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
    data_adjust = adjust_database(MYSQL_SETTING, TABLE_NAME, TABLE_PRIMARY_KEY, IP)

    if data_adjust:
        logger.debug('Mysql adjusted data:\n{}'.format(data_adjust))
        logger.debug('Mysql data reindex success.')
except:
    logger.exception('Error occur while database reindexing.\n')
    logger.critical('Program stopped.')
    sys.exit()


# 開始抓資料,一個IP一條thread
try:
    thread_pool = []
    for ip in IP:
        thread_pool.append(threading.Thread(target=fetch_task, args=[TARGET_MSSQL_SETTING_LIST[ip], DATA_COUNT, ]))
    for i in thread_pool:
        i.start()
    for i in thread_pool:
        i.join()
except:
    logger.exception('Error occur while doing monit tasks.\n')


try:
    with mysql.connector.connect(**MYSQL_SETTING) as connector:
        cursor = connector.cursor()
        cursor.execute('use cacti_customize;')
        # 逐個ip寫入
        for ip in IP:
            # SQL command字串處理
            column_list = Data[ip].keys()
            SQL_command = 'UPDATE {} SET '.format(TABLE_NAME)
            for row in column_list:
                SQL_command += '{} = {}, '.format(row, Data[ip][row])
            SQL_command = SQL_command.strip().strip(',')
            SQL_command += " WHERE IP = '{}';".format(ip)
            # 執行SQL cmd
            cursor.execute(SQL_command)
        connector.commit()
        cursor.close()
    logger.debug('Mysql data update success. Updated data count:{}'.format(len(IP)))
except Exception as e:
    logger.warning('Error occur while update data to MySQL.\n'+str(e))