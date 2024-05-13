-Develop python version:3.9.1
-Library installed:
    pip install requests
    pip install mysql-connector-python


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

CREATE TABLE webLatency (
url VARCHAR(500) PRIMARY KEY,
keyword VARCHAR(500),
latency INT,
timeout FLOAT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


注意事項:
1.此程式需要在事件排程器中設定每五分鐘執行一次
2.<timeoutSetting></timeoutSetting>不可超過240
