<?php
error_reporting(0);

if (!isset($called_by_script_server)) {
	include_once(dirname(__FILE__) . '/../include/cli_check.php');
	include_once(dirname(__FILE__) . '/../lib/snmp.php');

	array_shift($_SERVER['argv']);

	print call_user_func_array('ss_webLatency', $_SERVER['argv']);
} else {
	include_once(dirname(__FILE__) . '/../lib/snmp.php');
}

function ss_webLatency($hostname = '', $host_id = 0, $snmp_auth = '', $cmd = 'index', $arg1 = '', $arg2 = '') {
    $snmp = explode(':', $snmp_auth);
	$snmp_version   = $snmp[0];
	$snmp_port      = $snmp[1];
	$snmp_timeout   = $snmp[2];
	$ping_retries   = $snmp[3];
	$max_oids       = $snmp[4];

	$snmp_auth_username   = '';
	$snmp_auth_password   = '';
	$snmp_auth_protocol   = '';
	$snmp_priv_passphrase = '';
	$snmp_priv_protocol   = '';
	$snmp_context         = '';
	$snmp_community       = '';
    $PATH_TO_CONFIG = 'C:/Apache24/htdocs/cacti/expertos/';    

	if ($snmp_version == 3) {
		$snmp_auth_username   = $snmp[6];
		$snmp_auth_password   = $snmp[7];
		$snmp_auth_protocol   = $snmp[8];
		$snmp_priv_passphrase = $snmp[9];
		$snmp_priv_protocol   = $snmp[10];
		$snmp_context         = $snmp[11];
	} else {
		$snmp_community = $snmp[5];
	}
    $webLatency_config = simplexml_load_file($PATH_TO_CONFIG.'WebLatency_config.xml');
    $host = $webLatency_config->dbSetting->host;
    $user = $webLatency_config->dbSetting->user;
    $pwd = $webLatency_config->dbSetting->pwd;
    $database = $webLatency_config->dbSetting->database;
    $table = $webLatency_config->dbSetting->table;
    if ($cmd=='index'){
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            while ($row = $result->fetch_assoc()){
                print $row['url']."\n";
            }
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
    }
    else if ($cmd=='num_indexes'){      
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            print $result->num_rows;
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
    }
    else if ($cmd== "query"){
        $arg = $arg1;
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            while ($row = $result->fetch_assoc()){
                print $row['url']."!".$row[$arg]."\n";
            }
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
    }
    else if ($cmd == "get"){
        $arg = $arg1;
        $index = $arg2;
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = "SELECT ".$arg." FROM ". $table. " WHERE url='".$index."'";
            $result = $conn->query($sql_command)->fetch_all()[0][0];
            return $result;
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
    }
}
