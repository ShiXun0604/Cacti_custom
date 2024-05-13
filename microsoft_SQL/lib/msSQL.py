import pymssql, time
from queue import Queue
from lib.msSQL_cmd import *


global Data
Data = {}

def fetch_task(MSSQL_SETTING, DATA_COUNT):
    # 連接到 SQL Server
    conn = pymssql.connect(**MSSQL_SETTING)
    cursor = conn.cursor()
    ip = MSSQL_SETTING['server']


    start_time = time.time()
    # -------- DB連線數 --------
    SQL_command = SQL_COMMAND_1
    cursor.execute(SQL_command)  
    data = cursor.fetchall()[0][0]
    Data[ip]['conn_count'] = data
    
    exec_time = (time.time() - start_time)*1000
    # -------- 等待中的task數量 --------
    SQL_command = SQL_COMMAND_2
    cursor.execute(SQL_command)  
    data = cursor.fetchall()[0][0]
    Data[ip]['waiting_task_count'] = data
    
    # -------- CPU用量 --------
    SQL_command = SQL_COMMAND_3
    cursor.execute(SQL_command)  
    # 回傳型態:[(),()], 第一個為default, 第二個為internal, tuple的第6向為結果值
    data1, data2 = cursor.fetchall()
    Data[ip]['default_cpu'] = data1[6]
    Data[ip]['internal_cpu'] = data2[6]

    # -------- Memory usage --------
    SQL_command = SQL_COMMAND_4
    cursor.execute(SQL_command) 
    cursor.fetchall()
    cursor.fetchall()
    data = cursor.fetchall()
    target_server_memory = data[0][1]
    maximum_workspace_memory = data[1][1]
    
    for row in data:
        if 'Total Server Memory' in row[0]:
            total_server_memory = row[1]
    
    Data[ip]['target_server_memory'] = target_server_memory
    Data[ip]['maximum_workspace_memory'] = maximum_workspace_memory
    Data[ip]['total_server_memory'] = total_server_memory

    # -------- SQL Top10 command --------
    SQL_command = SQL_COMMAND_5
    cursor.execute(SQL_command)
    data = cursor.fetchall()
    try:
        Data[ip]['exec_count_1'] = data[0][0]
        Data[ip]['avrg_times_1'] = data[0][1]
    except:
        Data[ip]['exec_count_1'] =  'NULL'
        Data[ip]['avrg_times_1'] =  'NULL'
    try:
        Data[ip]['exec_count_2'] = data[1][0]
        Data[ip]['avrg_times_2'] = data[1][1]
    except:
        Data[ip]['exec_count_2'] =  'NULL'
        Data[ip]['avrg_times_2'] =  'NULL'
    try:    
        Data[ip]['exec_count_3'] = data[2][0]
        Data[ip]['avrg_times_3'] = data[2][1]
    except:
        Data[ip]['exec_count_3'] =  'NULL'
        Data[ip]['avrg_times_3'] =  'NULL'
    # -------- 資料庫回應延遲 --------
    Data[ip]['delay_time'] = exec_time



    # 關閉游標和連接
    cursor.close()
    conn.close()