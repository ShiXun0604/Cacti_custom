import win32serviceutil, win32service, win32event, servicemanager, time
import threading, sys
from lib.log import *
from lib.MySQL_query import *
from lib.ping_lib import *
from lib.queue_lib import *


class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Cacti_PingLatency"
    _svc_display_name_ = "Cacti_PingLatency"
    _svc_description_ = "This is python daemon script"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        WRITING_TIME = 4
        # WRITING_TIME = time.localtime().tm_min #  for test
        CONFIG_FILE_PATH = 'C:\cacti_expertos\PingLatency\PingLatency_config.xml'
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
            IP = []
            for ele in config.find('targetList'):
                ip = ele.find('IP').text
                IP.append(ip)
                ping_queue[ip] = Queue()
                lock[ip] = Lock()            

            # Load monitor settings
            monitor_setting = config.find('monitorConfig')
            AVERAGE_INTERVAL = int(monitor_setting.find('averageInterval').text)
            LANGUAGE = monitor_setting.find('systemLanguage').text
            LOG_PATH = monitor_setting.find('logPath').text
            RESULT_COUNT = 300/AVERAGE_INTERVAL
            
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
            
        
        # Main nonestop while loop
        flag = False
        while not win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
            min = time.localtime().tm_min
            sec = time.localtime().tm_sec

            # ----- Time to execute monit tasks -----
            if sec%AVERAGE_INTERVAL == 0:
                # monit task start
                try:
                    thread_pool = []
                    for ip in IP:
                        thread_pool.append(threading.Thread(target=ping_and_save,args=[ip, RESULT_COUNT ]))
                    for i in thread_pool:
                        # All threads wiil end in 10 seconds
                        i.start()  
                    for i in thread_pool:
                        i.join()
                    # log_append(log_text='Monit tasks done.')
                except:
                    logger.exception('Error occur while doing monit tasks.\n')
                    #log_append(type='WARNING', log_text='Error occur while doing monit tasks.\n' + str(e))
            
            # ----- Time to update database. After update database, reindex and reset IPs. -----
            if not flag and min%5 == WRITING_TIME:
                flag = True
            elif flag and min%5 == (WRITING_TIME+1)%5:
                flag = False

                # reset log name
                del logger
                logger = logging.getLogger()
                current_datetime = datetime.datetime.now()
                log_filepath = '{}\{}_{}.txt'.format(LOG_PATH, TABLE_NAME, current_datetime.strftime("%Y-%m-%d"))
                set_logger_filepath(logger, log_filepath)

                
                # write monit data to MySQL
                try:
                    # update into database
                    with mysql.connector.connect(**MYSQL_SETTING) as connector:
                        cursor = connector.cursor()
                        logger.debug('MySQL login successful.')
                        for ip in IP:
                            # reading queue data
                            lock[ip].acquire()
                            average, err = calculate_average(ping_queue[ip])
                            lock[ip].release()
                            # SQL command
                            SQL_command = "UPDATE {} SET latency = {} WHERE {} = '{}';".format(TABLE_NAME, average, TABLE_PRIMARY_KEY, ip)
                            cursor.execute(SQL_command)
                            SQL_command = "UPDATE {} SET faliure = {} WHERE {} = '{}';".format(TABLE_NAME, err, TABLE_PRIMARY_KEY, ip)
                            cursor.execute(SQL_command)
                            
                        connector.commit()
                        cursor.close()

                    logger.debug('Mysql data update success. Updated data count:{}'.format(len(IP)))
                except Exception as e:
                    logger.warning('Error occur while update data to MySQL.\n'+str(e))

                # --- reindexing --- 
                # reloads target IPs
                try:
                    IP = []
                    with open(CONFIG_FILE_PATH, 'rb') as f:
                        config = ET.fromstring(f.read().decode('utf-8'))
                        for ele in config.find('targetList'):
                            IP.append(ele.find('IP').text)
                except:
                    logger.exception('Error occur while reloading config file.\n')
                    logger.critical('Program stopped.')
                    sys.exit()
                
                # Adjust current IP list and associate data
                try:
                    old_IP = ping_queue.keys()
                    for ip in IP:
                        if ip not in old_IP:
                            ping_queue[ip] = Queue()
                            lock[ip] = Lock()
                    del_IPs = []
                    for old_ip in old_IP:
                        if old_ip not in IP:
                            del_IPs.append(old_ip)
                    for old_ip in del_IPs:
                        del ping_queue[old_ip]
                        del lock[old_ip]
                except:
                    logger.exception('Error occur while reindexing IP list and associate data.\n')
                    logger.critical('Program stopped.')
                    sys.exit()

                # database reindexing
                try:
                    data_adjust = adjust_database(MYSQL_SETTING, TABLE_NAME, TABLE_PRIMARY_KEY, IP)
                    if data_adjust:
                        logger.debug('MySQL login successful.')
                        logger.debug('Mysql adjusted data:\n{}'.format(data_adjust))
                        logger.debug('Mysql data reindex success.')
                except:
                    logger.exception('Error occur while database reindexing.\n')
                    logger.critical('Program stopped.')
                    sys.exit()
                
            time.sleep(1)
        logger.critical('Program stopped.')


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PythonService)