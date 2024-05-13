import pymssql, time
import xml.etree.ElementTree as ET
from msSQL_cmd import *

MSSQL_SETTING = {}
# 將config檔讀入
with open('C:\cacti_expertos\microsoftSQL\microsoftSQL_config.xml', 'rb') as f:
    # 讀進cacti mysql設定
    config = ET.fromstring(f.read().decode('utf-8'))

# 讀進待測microsoft SQL資料
for ele in config.find('targetList'):
    svr_IP = ele.find('IP').text
    MSSQL_SETTING = {
        'server':svr_IP,
        'user' : ele.find('user').text,
        'password' : ele.find('pwd').text,
    }

conn = pymssql.connect(**MSSQL_SETTING)
cursor = conn.cursor()

SQL_command = SQL_COMMAND_4

start_time = time.time()
cursor.execute(SQL_command)
exec_time = (time.time() - start_time)*1000  
cursor.fetchall()
cursor.fetchall()
data = cursor.fetchall()
print(data)
print(len(data))
#print(exec_time)



cursor.close()
conn.close()