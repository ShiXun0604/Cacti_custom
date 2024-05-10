import threading, datetime, sys
from threading import Lock
from lib.db_query import *
from lib.RestAPI import *
from lib.log import *



start_time = time.time()
# ----- DECLARE CONSTANT VARIABLES -----
# Loads the config file
CONFIG_FILE_PATH = 'C:\cacti_expertos\datacore\Datacore_config.xml'
with open(CONFIG_FILE_PATH, 'rb') as f: 
    config = ET.fromstring(f.read().decode('utf-8'))
Mysql_config = config.find('MysqlSetting')

# NAME_TO_IP
NAME_TO_IP = {}
for datacore in config.find('serverGroup'):
    ip = datacore.find('IP').text
    name = datacore.find('name').text
    NAME_TO_IP[name] = ip

# API query server
QUERY_IP = config.find('APIqueryServer').find('IP').text
Authorization = config.find('APIqueryServer').find('Authorization').text

# Trying setting
TRYING_COUNT = int(config.find('monitorConfig').find('tryingCount').text)
TRYING_INTERVAL = float(config.find('monitorConfig').find('tryingInterval').text)

# Log related
LOG_PATH = config.find('monitorConfig').find('logPath').text

# Mysql setting
MYSQL_SETTING = {
    "host" : Mysql_config.find('host').text,
    "user": Mysql_config.find('user').text, 
    "password" : Mysql_config.find('pwd').text,
    "database" : Mysql_config.find('database').text,
}

# construct logger
logger = logging.getLogger()
current_datetime = datetime.datetime.now()
log_filepath = '{}\datacore_{}.txt'.format(LOG_PATH, current_datetime.strftime("%Y-%m-%d"))
set_logger_filepath(logger, log_filepath)
logger_lock = Lock()



logger.info('*****Program started*****')
# ----- MYSQL TESTING -----
try:
    with mysql.connector.connect(**MYSQL_SETTING) as connector:
        cursor = connector.cursor()
        SQL_command = 'SHOW TABLES;'
        cursor.execute(SQL_command)

        data = cursor.fetchall()
        #print(data)

        connector.commit()
        cursor.close()
except:
    logger.critical('MySQL setting error. Program stopped.')
    sys.exit()


# ----- REINDEXING REINDEXING REINDEXING -----
# If error count touch limit, stop the program.
if APIcall_ErrCnt > ERROR_COUNT_LIMIT:
    logger.critical('Already touch the limit of error count. Program stopped.')
    sys.exit()

# Use query server for loop to index monit targets
headers = {
    'ServerHost': ip,
    'Authorization': Authorization,
}
url = 'https://{ip}/RestService/rest.svc/1.0/monitors'.format(ip=QUERY_IP)
response = requests.get(url, headers=headers, verify=False).text
data = json.loads(response)

# reindexing every kind of targets in API(ip_name->id)
TARGET_SCSI_PORTS = {}
TARGET_DATACORE_SERVER = {}
TARGET_DISK_POOLS = {}
TARGET_HOSTS = {}
TARGET_PHYSICAL_DISKS = {}
TARGET_POOL_PHYSICAL_DISKS = {}
TARGET_VIRTUAL_DISKS = {}
TARGET_POOL_VIRTUAL_DISK_SOURCES = {}
TARGET_MIRRORING = {}
# poolVirtualDiskPool temp dict(id->ip_name)
temp_all_poolVtualDiskSource = {}
temp_CDP_poolVtualDiskSource = {}

# error occur
if response[0] == '{':
    error_add_one()
    # write into log
    err_msg = data['Message']
    logger.critical('Error occure while reindexing. Error message:{}'.format(err_msg))
    sys.exit()
# reindexing
else:
    for row in data:
        # ----- Server SCSI port -----
        if 'ServerFcPortStateMonitor' in row['TemplateId']:
            #print(row)
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')[6:]

                targetName = ''
                for i in range(len(Name)-2):
                    if Name[i]:
                        targetName += Name[i] + '_'
                targetName = targetName.strip('_')

                ip = NAME_TO_IP[Name[len(Name)-1]]
                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_SCSI_PORTS[ip_name] = id
            except:
                # logging.exception('error occured in Server SCSI port indexing part')
                pass
        elif 'ServeriScsiPortStateMonitor' in row['TemplateId']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')
                targetName = Name[5:len(Name)-2]

                name = ''
                for i in targetName:
                    name += i+'_'
                name = name.strip('_')

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}({})'.format(ip, name, Name[len(Name)-1])

                TARGET_SCSI_PORTS[ip_name] = id
            except:
                # logging.exception('error occured in Server SCSI port indexing part')
                pass
        # ----- Datacore servers -----       
        elif 'ServerMachineStateMonitor' in row['TemplateId']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[4]

                ip = NAME_TO_IP[targetName]

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_DATACORE_SERVER[ip_name] = id
            except:
                # logging.exception('error occured in datacore servers indexing part')
                pass
        # ----- Disk pools -----
        elif 'PoolDepletionMonitor' in row['TemplateId']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[5]

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_DISK_POOLS[ip_name] = id
            except:
                # logging.exception('error occured in datacore servers indexing part')
                TARGET_POOL_VIRTUAL_DISK_SOURCES
        # ----- Hosts -----
        elif 'ClientMachineStateMonitor' in row['TemplateId']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[len(Name)-1]

                ip = headers['ServerHost']

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_HOSTS[ip_name] = id
            except:
                # logging.exception('error occured in hosts indexing part')
                pass
        # ----- Physical disks -----
        elif 'PhysicalDiskStateMonitor' in row['TemplateId'] and row['MonitoredObjectId'][0] == '{':
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[len(Name)-3]

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_PHYSICAL_DISKS[ip_name] = id
            except:
                # logging.exception('error occured in physical disks indexing part')
                pass
        # ----- Pool physical disks -----
        elif 'PoolMemberStateMonitor' in row['TemplateId']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[len(Name)-3]

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_POOL_PHYSICAL_DISKS[ip_name] = id
            except:
                # logging.exception('error occured in pool physical disks indexing part')
                pass
        # ----- Pool virtual disks source -----
        elif 'Virtual Disk Source' in row['ExtendedCaption']:
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')
                #print('{}'.format(id, ))
                #print('{:20}{}'.format(row['Caption'], row['ExtendedCaption']))
                #print(row)
                targetName = Name[len(Name)-3]

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}'.format(ip, targetName)

                temp_all_poolVtualDiskSource[id] = ip_name
                if 'Storage source from' in row['ExtendedCaption']:
                    temp_CDP_poolVtualDiskSource[id] = ip_name
            except Exception as e:
                #　logging.exception('error occured in pool virtual disks indexing part')
                pass
        # ----- Virtual disks -----
        elif 'virtual disk' in row['Description']:
            # virtual disk must behind the pool virtual disks source
            try:
                # String processing -> Deal with the string in row['MonitoredObjectId'] to get ip,id,targetname
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[len(Name)-4]

                ip = headers['ServerHost']

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_VIRTUAL_DISKS[ip_name] = id
            except:
                #　logging.exception('error occured in virtual disks indexing part')
                pass
        # ----- Mirroring -----
        elif 'V.' in row['MonitoredObjectId']:
            try:
                id = row['MonitoredObjectId']
                Name = row['ExtendedCaption'].split(' ')

                targetName = Name[len(Name)-3]

                ip = NAME_TO_IP[Name[len(Name)-1]]

                ip_name = '{}/{}'.format(ip, targetName)

                TARGET_MIRRORING[ip_name] = id
                
            except:
                #　logging.exception('error occured in virtual disks indexing part')
                pass


# deal with Pool virtual disks source CDP(continuous data protection)
for id in temp_CDP_poolVtualDiskSource.keys():
    ip, name = temp_all_poolVtualDiskSource[id].split('/')
    name = 'log_history_of_' + name
    ip_name = '{}/{}'.format(ip, name)

    temp_all_poolVtualDiskSource[id] = ip_name

for id in temp_all_poolVtualDiskSource.keys():
    ip_name = temp_all_poolVtualDiskSource[id]
    TARGET_POOL_VIRTUAL_DISK_SOURCES[ip_name] = id

# reindex result
#print(TARGET_SCSI_PORTS)
#print(TARGET_DATACORE_SERVER)
#print(TARGET_DISK_POOLS)
#print(TARGET_HOSTS)
#print(TARGET_PHYSICAL_DISKS)
#print(TARGET_POOL_PHYSICAL_DISKS)
#print(TARGET_VIRTUAL_DISKS)
#print(TARGET_POOL_VIRTUAL_DISK_SOURCES)
#print(TARGET_MIRRORING)

# ----- CONSTRUCT MONIT CASK CLASSES -----
MonitTask_pool = []
# datacore servers
datacoreServers = MonitTask(CONFIG_FILE_PATH, 'datacoreServers', TARGET_DATACORE_SERVER)
MonitTask_pool.append(datacoreServers)
# disk pools
diskPools = MonitTask(CONFIG_FILE_PATH, 'diskPools', TARGET_DISK_POOLS)
MonitTask_pool.append(diskPools)
# hosts
hosts = MonitTask(CONFIG_FILE_PATH, 'hosts', TARGET_HOSTS)
MonitTask_pool.append(hosts)
# Physical disks
physicalDisks = MonitTask(CONFIG_FILE_PATH, 'physicalDisks', TARGET_PHYSICAL_DISKS)
MonitTask_pool.append(physicalDisks)
# pool physical disks
poolPhysicalDisks = MonitTask(CONFIG_FILE_PATH, 'poolPhysicalDisks', TARGET_POOL_PHYSICAL_DISKS)
MonitTask_pool.append(poolPhysicalDisks)
# pool virtual disks source
poolVirtualDiskSources = MonitTask(CONFIG_FILE_PATH, 'poolVirtualDiskSources', TARGET_POOL_VIRTUAL_DISK_SOURCES)
MonitTask_pool.append(poolVirtualDiskSources)
# server SCSI ports
serverSCSIports = MonitTask(CONFIG_FILE_PATH, 'serverSCSIports', TARGET_SCSI_PORTS)
MonitTask_pool.append(serverSCSIports)
# virtual disks
virtualDisks = MonitTask(CONFIG_FILE_PATH, 'virtualDisks', TARGET_VIRTUAL_DISKS)
MonitTask_pool.append(virtualDisks)
# mirroring
mirroring = MonitTask(CONFIG_FILE_PATH, 'mirroring', TARGET_MIRRORING)
MonitTask_pool.append(mirroring)

# test
#datacoreServers.reset_AUTH('Basic administrator 1qaz#EDC')
#hosts.execute_task(logger, TRYING_COUNT, TRYING_INTERVAL)

# ----- EXCECUTE MONIT TASK -----
def task(monitTask, logger):
    # Execute task
    try:
        monitTask.execute_task(logger, TRYING_COUNT, TRYING_INTERVAL)
    except:
        # LOG->Record message into log
        logger_lock.acquire()
        log_string = '------{}------'.format(monitTask.TABLE_NAME)
        logger.debug(log_string)

        logger.warning('Error occure while doing monit task')
        logger.exception('Error message:')
        logger_lock.release()

# Execute tasks in parallel    
thread_pool = []
for monitTask in MonitTask_pool:
    thread_pool.append(threading.Thread(target=task, args=[monitTask, logger]))
for thread in thread_pool:
    thread.start()
    time.sleep(0.5)
for thread in thread_pool:
    thread.join()

# LOG->SQL cmd and API call stats
SQLcmd_stats, API_stats, monitID_stats = 0, 0, 0
for monitTask in MonitTask_pool:
    SQLcmd_stats += monitTask.SQL_query_count
    API_stats += monitTask.API_query_count
    monitID_stats += len(monitTask.TARGET_DICT.keys())

log_string = 'Total target monit ID count:{}'.format(monitID_stats)
logger.debug(log_string)
log_string = 'Total executed API call count:{}'.format(API_stats)
logger.debug(log_string)
log_string = 'Total executed SQL command count:{}'.format(SQLcmd_stats)
logger.debug(log_string)

# LOG->Executed time
execute_time = time.time() - start_time
logger.info('Monit done. Excecute time:{} second'.format(execute_time))