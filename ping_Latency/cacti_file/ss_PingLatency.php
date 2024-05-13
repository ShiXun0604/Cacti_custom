#!/usr/bin/env php
<?php
# error_reporting(0);

if (!isset($called_by_script_server)) {
	include_once(dirname(__FILE__) . '/../include/cli_check.php');
	include_once(dirname(__FILE__) . '/../lib/snmp.php');

	array_shift($_SERVER['argv']);

	print call_user_func_array('ss_pingLatency', $_SERVER['argv']);
} else {
	include_once(dirname(__FILE__) . '/../lib/snmp.php');
}

function ss_pingLatency($hostname = '', $host_id = 0, $snmp_auth = '', $cmd = 'index', $arg1 = '', $arg2 = '') {
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
	$pingLatency_config = simplexml_load_file($PATH_TO_CONFIG.'PingLatency_config.xml');
	$host = $pingLatency_config->dbSetting->host;
    $user = $pingLatency_config->dbSetting->user;
    $pwd = $pingLatency_config->dbSetting->pwd;
    $database = $pingLatency_config->dbSetting->database;
    $table = $pingLatency_config->dbSetting->table;

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

	

	if ($cmd == 'index') {
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            while ($row = $result->fetch_assoc()){
                print $row['IP']."\n";
            }
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
	} 
	elseif ($cmd == 'num_indexes') {
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
	elseif ($cmd == 'query') {
		$arg = $arg1;
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            while ($row = $result->fetch_assoc()){
                print $row['IP']."!".$row[$arg]."\n";
            }
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
	} 
	elseif ($cmd == 'get'){
        $arg = $arg1;
        $index = $arg2;
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
        
            $sql_command = "SELECT ".$arg." FROM ". $table. " WHERE IP='".$index."'";
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

