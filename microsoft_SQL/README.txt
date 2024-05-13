-Develop python version:3.9.1
-Library installed:
    pip install pymssql


-Database
程式需要MySQL使用者,使用的帳號密碼為
使用者:ShiXun
密碼:password


1.若MySQL沒有使用者'ShiXun'請執行:
CREATE USER 'ShiXun'@'localhost' IDENTIFIED BY 'password';


2.若MySQL沒有Cacti_customize的database則執行:
CREATE DATABASE cacti_customize;
GRANT ALL PRIVILEGES ON cacti_customize.* TO 'ShiXun'@'localhost';


3.創建table
USE cacti_customize;

CREATE TABLE microsoftSQL (
IP VARCHAR(500) PRIMARY KEY,
conn_count FLOAT,
waiting_task_count FLOAT,
default_cpu FLOAT,
internal_cpu FLOAT,
delay_time FLOAT,
target_server_memory FLOAT,
maximum_workspace_memory FLOAT,
total_server_memory FLOAT,
avrg_times_1 BIGINT,
avrg_times_2 BIGINT,
avrg_times_3 BIGINT,
exec_count_1 BIGINT,
exec_count_2 BIGINT,
exec_count_3 BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

注意事項:
1.此程式需要在事件排程器中設定每五分鐘執行一次





msSQL筆記:
1.要開啟TCP(在SQL Server Management->)
