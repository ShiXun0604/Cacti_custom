-Develop python version:3.9.1
-Library installed:
    pip install requests
    pip install mysql-connector-python
    pip install pywin32


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

CREATE TABLE pingLatency (
IP VARCHAR(500) PRIMARY KEY,
latency FLOAT,
faliure INT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-注意事項
1. 此程式為windows service,請在cmd執行以下指令安裝windows服務
python main.py install 
python main.py --startup auto install 
python main.py start


-Log紀錄的事件
1. 程式啟動與停止的時間戳
2. mysql登入、新增、刪除操作(不包括更新)