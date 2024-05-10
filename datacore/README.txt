-Develop python version:3.9.1
-Library installed:
    pip install requests
    pip install mysql-connector-python



安裝建置流程：
Step1.設置MySQL使用者以及table

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

CREATE TABLE datacoredatacoreservers(
ip_name VARCHAR(400) PRIMARY KEY,
InitiatorReads BIGINT,
InitiatorWrites BIGINT,
InitiatorBytesRead BIGINT,
InitiatorBytesWritten BIGINT,
TargetBytesRead BIGINT,
TargetBytesWritten BIGINT,
TargetReads BIGINT,
TargetWrites BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
CacheReadHitBytes BIGINT,
CacheReadMissBytes BIGINT,
CacheWriteHitBytes BIGINT,
CacheWriteMissBytes BIGINT,
DeduplicationRatioPercentage BIGINT,
CompressionRatioPercentage BIGINT,
MirrorTargetMaxIOTime BIGINT,
ReplicationBytesToSend BIGINT,
ReplicationBufferPercentFreeSpace BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacoreDiskPools(
ip_name VARCHAR(400) PRIMARY KEY,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
TotalReadTime BIGINT,
TotalWriteTime BIGINT,
AverageReadTime FLOAT,
AverageWriteTime FLOAT,
TotalBytesMigrated BIGINT,
PercentAllocated FLOAT,
BytesTotal BIGINT,
BytesAllocated BIGINT,
BytesInReclamation BIGINT,
BytesAllocatedPercentage INT,
BytesReservedPercentage INT,
BytesInReclamationPercentage INT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacoreHosts(
ip_name VARCHAR(400) PRIMARY KEY,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesProvisioned BIGINT,
MaxReadSize BIGINT,
MaxWriteSize BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacorePhysicalDisks(
ip_name VARCHAR(400) PRIMARY KEY,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
TotalReadsTime BIGINT,
TotalWritesTime BIGINT,
AverageReadsTime FLOAT,
AverageWritesTime FLOAT,
AverageQueueLength FLOAT,
TotalPendingCommands BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacorePoolPhysicalDisks(
ip_name VARCHAR(400) PRIMARY KEY,
BytesAllocated BIGINT,
BytesAvailable BIGINT,
BytesInReclamation BIGINT,
BytesTotal BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacorePoolVirtualDiskSources(
ip_name VARCHAR(400) PRIMARY KEY,
CacheReadHitBytes BIGINT,
CacheReadMissBytes BIGINT,
CacheWriteHitBytes BIGINT,
CacheWriteMissBytes BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
TotalReadTime BIGINT,
TotalWriteTime BIGINT,
AverageReadTime FLOAT,
AverageWriteTime FLOAT,
StreamBytesAllocated BIGINT,
StreamBytesUsed BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacoreSCSIports(
ip_name VARCHAR(400) PRIMARY KEY,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
LinkFailureCount BIGINT,
LossOfSyncCount BIGINT,
LossOfSignalCount BIGINT,
PrimitiveSeqProtocolErrCount BIGINT,
InvalidTransmissionWordCount BIGINT,
InvalidCrcCount BIGINT,
InitiatorReads BIGINT,
InitiatorWrites BIGINT,
InitiatorBytesRead BIGINT,
InitiatorBytesWritten BIGINT,
TargetReads BIGINT,
TargetWrites BIGINT,
TargetBytesRead BIGINT,
TargetBytesWritten BIGINT,
PendingInitiatorCommands BIGINT,
PendingTargetCommands BIGINT,
TotalPendingCommands BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacoreVirtualDisks(
ip_name VARCHAR(400) PRIMARY KEY,
PercentAllocated FLOAT,
CacheReadHitBytes BIGINT,
CacheReadMissBytes BIGINT,
CacheWriteHitBytes BIGINT,
CacheWriteMissBytes BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
ReplicationTimeLag FLOAT, 
ReplicationTimeDifference FLOAT, 
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE datacoreMirroring(
ip_name VARCHAR(400) PRIMARY KEY,
TotalReadsTime FLOAT,
TotalWritesTime BIGINT,
AverageReadsTime FLOAT,
AverageWritesTime FLOAT,
TotalPendingCommands BIGINT,
TotalReads BIGINT,
TotalWrites BIGINT,
TotalBytesRead BIGINT,
TotalBytesWritten BIGINT,
AverageQueueLength BIGINT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
last_modify TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

Step2.設置config檔
1.MysqlSetting基本不用動。
2.serverGroup內將已知datacore的server訊息寫入。
3.APIqueryServer內將呼叫目標的datacore訊息寫入。
4.monitorConfig根據需求做調整。
5.monitTarget請勿更動。

Step3.嘗試運行程式，沒問題的話在事件排程器將Datacore_execute.bat設定每五分鐘執行一次，最好將執行時間設在4,9,14,19,...。

Step4.將cacti_file內的檔案全數匯入cacti，該放哪就放哪，該載入就載入。

Step5.使用data query的方法在cacti內建立圖表。