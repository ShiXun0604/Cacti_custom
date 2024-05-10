import requests, urllib3, json, time, mysql.connector
import xml.etree.ElementTree as ET



# 禁用SSL驗證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Error count
global APIcall_ErrCnt, ERROR_COUNT_PATH, ERROR_COUNT_LIMIT
CONFIG_FILE_PATH = 'C:\cacti_expertos\datacore\Datacore_config.xml'
with open(CONFIG_FILE_PATH, 'rb') as f: 
    config = ET.fromstring(f.read().decode('utf-8'))

# logger
ERROR_COUNT_PATH = config.find('monitorConfig').find('errorCountPath').text
ERROR_COUNT_LIMIT = int(config.find('monitorConfig').find('errorCountLimit').text)
with open(ERROR_COUNT_PATH, 'r') as f:
    APIcall_ErrCnt = int(f.read())



def error_add_one():
    global APIcall_ErrCnt, ERROR_COUNT_LIMIT
    APIcall_ErrCnt += 1
    with open(ERROR_COUNT_PATH, 'w') as f:
        f.write(str(APIcall_ErrCnt))



class MysqlSetting():
    def __init__(self, MYSQL_SETTING, TABLE_NAME, TABLE_COLUMNS):
        # SQL setting
        self.__MYSQL_SETTING = MYSQL_SETTING
        self.TABLE_NAME = TABLE_NAME
        self.TABLE_COLUMNS = TABLE_COLUMNS
    
    def ext_MYSQL_SETTING(self):
        return self.__MYSQL_SETTING

    def adjust_database(self, item_list):
        with mysql.connector.connect(**self.__MYSQL_SETTING) as connector:
            cursor = connector.cursor()

            # 檢查DB監測對象是否跟config相同(雙向檢查) 
            cursor.execute("SELECT * FROM {};".format(self.TABLE_NAME))
            db_item_list = []
            record = ''
            for row in cursor.fetchall():
                db_item = row[0]
                if db_item not in item_list:
                    SQL_command = "DELETE from {} where ip_name='{}';".format(self.TABLE_NAME, db_item)
                    record += '{}\n'.format(SQL_command)
                    cursor.execute(SQL_command)
                    continue
                db_item_list.append(db_item)

            for item in item_list:
                if item not in db_item_list:
                    SQL_command = "INSERT INTO {} (ip_name) VALUES ('{}');".format(self.TABLE_NAME, item)
                    record += '{}\n'.format(SQL_command)
                    cursor.execute(SQL_command)
            connector.commit()
            cursor.close()
        return record



class MonitTask(MysqlSetting):
    def __init__(self, CONFIG_FILE_PATH, taskname, TARGET_DICT) -> None:
        # Load config file and create objects
        with open(CONFIG_FILE_PATH, 'rb') as f: 
            config = ET.fromstring(f.read().decode('utf-8'))
        task_config = config.find('monitTarget').find(taskname)
        Mysql_config = config.find('MysqlSetting')
        monitor_config = config.find('monitorConfig')
            
        # MySQL setting
        MYSQL_SETTING = {
            "host" : Mysql_config.find('host').text,
            "user": Mysql_config.find('user').text, 
            "password" : Mysql_config.find('pwd').text,
            "database" : Mysql_config.find('database').text,
        }
        TABLE_NAME = task_config.find('tableName').text
        
        # Monit related
        TABLE_COLUMNS = []
        for column in task_config.find('column'):
            TABLE_COLUMNS.append(column.text)

        CHECK_POINT = task_config.find('checkPoint').text
        MONIT_IP = config.find('APIqueryServer').find('IP').text
        AUTH = config.find('APIqueryServer').find('Authorization').text
        ERROR_COUNT_PATH = monitor_config.find('errorCountPath').text

        # Log setting
        RECORD_TARGET_COUNT = monitor_config.find('recordTargetCount').text
        RECORD_SQL_COMMAND = monitor_config.find('recordSQLcommand').text
        RECORD_SQL_COUNT = monitor_config.find('recordSQLcount').text
        RECORD_API_COUNT = monitor_config.find('recordAPIcount').text

        # average
        CALCU_AVRG_DICT = {}  # dict[column(average...)]['numerator'or'denominator'] = column
        if task_config.find('calcuAvrg'):
            for item in task_config.find('calcuAvrg'):
                column = item.find('column').text
                CALCU_AVRG_DICT[column] = {
                    'denominator' : item.find('denominator').text,
                    'numerator' : item.find('numerator').text,
                }

        # sum
        CALCU_SUM_DICT = {}  # dict[column(total...)] = list of column will sum together
        if task_config.find('calcuSum'):
            for sum in task_config.find('calcuSum'):
                column = sum.find('column').text
                CALCU_SUM_DICT[column] = []
                for item in sum.findall('item'):
                    CALCU_SUM_DICT[column].append(item.text)

        super().__init__(MYSQL_SETTING, TABLE_NAME, TABLE_COLUMNS)
        self.taskname = taskname
        self.__CHECK_POINT = CHECK_POINT
        self.__MONIT_IP = MONIT_IP
        self.__AUTH = AUTH
        self.TARGET_DICT = TARGET_DICT              # dict[ip_name] = id
        self.CALCU_AVRG_DICT = CALCU_AVRG_DICT      # dict[column(average...)]['numerator'or'denominator'] = column
        self.CALCU_SUM_DICT = CALCU_SUM_DICT        # dict[column(total...)] = list of column will sum together
        # result
        self.result = {}                            # dict[ip_name][column] = result
        self.average_result = {}                    # dict[ip_name][column] = result
        self.sum_result = {}                        # dict[ip_name][column] = result
        # log use message
        self.SQL_query_count = 0
        self.SQLcmd_executed = ''
        self.API_query_count = 0
        # log setting('True'or'False')
        self.RECORD_SQL_COMMAND = RECORD_SQL_COMMAND  
        self.RECORD_SQL_COUNT = RECORD_SQL_COUNT
        self.RECORD_API_COUNT = RECORD_API_COUNT
        self.RECORD_TARGET_COUNT = RECORD_TARGET_COUNT
        # API error
        self.ERROR_COUNT_PATH = ERROR_COUNT_PATH
        self.err_msgs = ''

        for ip_name in TARGET_DICT.keys():
            self.result[ip_name] = None
            self.average_result[ip_name] = None
            self.sum_result[ip_name] = None
    
    # for API error test
    def reset_AUTH(self, AUTH):
        self.__AUTH = AUTH
    

    def oneID_API_call(self, id):
        url = 'https://{ip}/RestService/rest.svc/1.0/performance/{id}'.format(ip=self.__MONIT_IP, id=id)
        headers = {
            "ServerHost": self.__MONIT_IP,
            "Authorization": self.__AUTH,
        }
        #print('{}\t{}'.format(APIcall_ErrCnt, self.taskname))
        if APIcall_ErrCnt < ERROR_COUNT_LIMIT:
            response = requests.get(url, headers=headers, verify=False).text
            self.API_query_count += 1
            if response[0] == '[':
                data = json.loads(response)[0]
                return data
            else:
                # API ERROR OCCURE!
                data = json.loads(response)
                self.err_msgs += data['Message'] + '\n'
                error_add_one()
                return False
        else:
            return False
    
    def log_write(self, logger):
        log_string = ''
        if self.RECORD_TARGET_COUNT == 'True':
            log_string += 'Target monit id amount:{}\n'.format(len(self.TARGET_DICT.keys()))
        if self.RECORD_SQL_COUNT == 'True':
            log_string += 'Executed SQL command amount:{}\n'.format(self.SQL_query_count)
        if self.RECORD_API_COUNT == 'True':
            log_string += 'Executed API call amount:{}\n'.format(self.API_query_count)
        if self.RECORD_SQL_COMMAND == 'True':
            log_string += 'Executed SQL commands:\n{}'.format(self.SQLcmd_executed).strip('\n')

        if log_string:
            log_string = '------{}------\n{}'.format(self.TABLE_NAME, log_string)
            logger.info(log_string)

        if self.err_msgs:
            err_string = 'Error occure in API call. Error message:{}\n'.format(self.err_msgs)
            logger.warning(err_string)
            


    # MAIN MONIT TASK CODE
    def execute_task(self, logger=None, TRYING_COUNT=5, TRYING_INTERVAL=1.5):
        # reindexing database
        self.adjust_database(self.result.keys())


        # establish the temp list of target, and prequery 1 time
        IP_Name = []
        for ip_name in self.TARGET_DICT.keys():
            # temprary target list
            IP_Name.append(ip_name)

            # prequery
            id = self.TARGET_DICT[ip_name]
            self.oneID_API_call(id)
        
        # Wait a moment to let datacore prepare data
        time.sleep(TRYING_INTERVAL)
        
        # Trying get valid data
        for i in range(TRYING_COUNT-1):           
            rm_list = []
            for ip_name in IP_Name:
                # API call
                id = self.TARGET_DICT[ip_name]
                data = self.oneID_API_call(id)                    
                
                if data == False:
                    # If touch API call error limit, set result = None
                    self.result[ip_name] = None
                elif data[self.__CHECK_POINT] != 0:
                    # if get avaliable data, add it to rm_list, delete it after loop
                    self.result[ip_name] = data
                    rm_list.append(ip_name)

            # Delete item from list which has valid data already
            for rm_item in rm_list:
                IP_Name.remove(rm_item)
            
            # If all id have data already, break out the loop.
            if len(IP_Name) == 0:
                break
            
            # Wait a moment, prevent waiting in last time doing loop.
            if i < TRYING_COUNT-2:
                time.sleep(TRYING_INTERVAL)
        
        # Calculate average
        if self.CALCU_AVRG_DICT:
            # fetch previous data from database
            previous_value_dict = {}
            with mysql.connector.connect(**self.ext_MYSQL_SETTING()) as connector:
                cursor = connector.cursor()
                for ip_name in self.result.keys():
                    previous_value_dict[ip_name] = {}
                    for item in self.CALCU_AVRG_DICT.keys():
                        # denominator
                        denominator = self.CALCU_AVRG_DICT[item]['denominator']
                        SQL_command = 'SELECT {} FROM {} WHERE ip_name="{}";'.format(denominator, self.TABLE_NAME, ip_name)
                        cursor.execute(SQL_command)
                        denominator_value = cursor.fetchall()[0][0]
                        previous_value_dict[ip_name][denominator] = denominator_value

                        # numerator
                        numerator = self.CALCU_AVRG_DICT[item]['numerator']
                        SQL_command = 'SELECT {} FROM {} WHERE ip_name="{}";'.format(numerator, self.TABLE_NAME, ip_name)
                        cursor.execute(SQL_command)
                        numerator_value = cursor.fetchall()[0][0]
                        previous_value_dict[ip_name][numerator] = numerator_value

                        self.SQL_query_count += 2

                connector.commit()
                cursor.close()

            # Calculate average
            self.average_result = {}
            for ip_name in self.result.keys():
                self.average_result[ip_name] = {}
                for column in self.CALCU_AVRG_DICT.keys():
                    denominator = self.CALCU_AVRG_DICT[column]['denominator']
                    numerator = self.CALCU_AVRG_DICT[column]['numerator']
                    
                    # if without valid data in result, write null and don't do the calculation
                    if self.result[ip_name] == None:
                        self.average_result[ip_name][column] = 'NULL'
                        continue
                    
                    a = self.result[ip_name][numerator]
                    b = previous_value_dict[ip_name][numerator]
                    c = self.result[ip_name][denominator]
                    d = previous_value_dict[ip_name][denominator]  

                    if (not b) and (not d):
                        self.average_result[ip_name][column] = 0
                    elif (c-d) == 0:
                        self.average_result[ip_name][column] = 0
                    else:
                        self.average_result[ip_name][column] = (a-b)/(c-d)

        # Calculate sum
        if self.CALCU_SUM_DICT:
            for ip_name in self.TARGET_DICT.keys():
                self.sum_result[ip_name] = {}
                for column in self.CALCU_SUM_DICT.keys():
                    # if without valid data in result, write null and don't do the calculation.
                    if self.result[ip_name] == None:
                        self.sum_result[ip_name][column] = 'NULL'
                        continue
                    
                    # Calculate sum
                    summary = 0
                    for sum_column in self.CALCU_SUM_DICT[column]:
                        summary += self.result[ip_name][sum_column]
                    self.sum_result[ip_name][column] = summary

        # Write result into database.
        with mysql.connector.connect(**self.ext_MYSQL_SETTING()) as connector:
            cursor = connector.cursor()
            # Loop through all ip_name and write value into DB
            #print(self.result)
            for ip_name in self.result.keys():
                # Establish SQL command(string)
                sql_partial_string = ''
                for column in self.TABLE_COLUMNS:
                    if column in self.CALCU_AVRG_DICT.keys():
                        # average
                        value = self.average_result[ip_name][column]
                    elif column in self.CALCU_SUM_DICT.keys():
                        # sum
                        value = self.sum_result[ip_name][column]
                    elif self.result[ip_name] == None:
                        # no data in result
                        value = 'NULL'
                    else:
                        # normal
                        value = self.result[ip_name][column]
                    sql_partial_string += '{}={}, '.format(column, value)
                sql_partial_string = sql_partial_string.strip().strip(',')

                # Excecute SQL command
                SQL_command = "UPDATE {} SET {} WHERE ip_name = '{}';".format(self.TABLE_NAME, sql_partial_string, ip_name)
                cursor.execute(SQL_command)
                
                # record SQL call info
                self.SQLcmd_executed += '\t{}\n'.format(SQL_command)
                self.SQL_query_count += 1

            connector.commit()
            cursor.close()
        
        # Log record
        if logger:
            self.log_write(logger)