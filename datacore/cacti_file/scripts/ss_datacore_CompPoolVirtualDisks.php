<?php
# error_reporting(0);

if (!isset($called_by_script_server)) {
	include_once(dirname(__FILE__) . '/../include/cli_check.php');
	include_once(dirname(__FILE__) . '/../lib/snmp.php');

	array_shift($_SERVER['argv']);

	print call_user_func_array('ss_datacore_CompPoolVirtualDisks', $_SERVER['argv']);
} else {
	include_once(dirname(__FILE__) . '/../lib/snmp.php');
}

function ss_datacore_CompPoolVirtualDisks($hostname = '', $host_id = 0, $snmp_auth = '', $cmd = 'index', $arg1 = '', $arg2 = '') {
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

    
    $PATH_TO_CONFIG = 'C:/cacti_expertos/datacore/';    
    $datacore_config = simplexml_load_file($PATH_TO_CONFIG.'Datacore_config.xml');
    $host = $datacore_config->MysqlSetting->host;
    $user = $datacore_config->MysqlSetting->user;
    $pwd = $datacore_config->MysqlSetting->pwd;
    $database = $datacore_config->MysqlSetting->database;

    # get virtualdisks array
    $table = $datacore_config->monitTarget->virtualDisks->tableName;
    try {
        # 建立連線和其他操作
        $conn = new mysqli($host, $user, $pwd, $database);
    
        $sql_command = 'SELECT * FROM '. $table;
        $result = $conn->query($sql_command);
        $virtual_disks = [];
        while ($row = $result->fetch_assoc()){
            list($ip, $name) = explode("/", $row['ip_name']);
            $virtual_disks[] = $name;
        }        
    } catch (Exception $e) {
        # 處理異常
        die("Error linking database: " . $conn->connect_error);
    } finally {
        # 釋放連線
        $conn->close();
    }
    # get datacore server group IP
    $svrs_obj = $datacore_config->serverGroup;
    $server1_IP = $svrs_obj->datacore[0]->IP;
    $server2_IP = $svrs_obj->datacore[1]->IP;
        

    # change to poolvirtualdisks table
    $table = $datacore_config->monitTarget->poolVirtualDiskSources->tableName;
    if ($cmd=='index'){
        foreach ($virtual_disks as $virtual_disk){
            print "{$virtual_disk}\n";
        }
        
    }
    else if ($cmd=='num_indexes'){      
        print sizeof($virtual_disks) . "\n";
    }
    else if ($cmd== "query"){
        $arg = $arg1;
        try {
            # 建立連線和其他操作
            $conn = new mysqli($host, $user, $pwd, $database);
            
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            
            $result_arr = [];
            while ($row = $result->fetch_assoc()){
                $result_arr[$row['ip_name']] = $row;                    
            }

            switch ($arg){
                case 'index':
                    foreach ($virtual_disks as $virtual_disk){
                        print "{$virtual_disk}!{$virtual_disk}\n";
                    }
                    break;
                # --- Desr ---
                case 'server1Desr':
                    foreach ($virtual_disks as $virtual_disk){
                        print "{$virtual_disk}!{$server1_IP}\n";
                    }
                    break;
                case 'server2Desr':
                    foreach ($virtual_disks as $virtual_disk){
                        print "{$virtual_disk}!{$server2_IP}\n";
                    }
                    break;
                # --- Average read time ---
                case 'averageReadTimeServer1':
                    foreach ($virtual_disks as $virtual_disk){
                        $virtual_disk_name = "{$server1_IP}/{$virtual_disk}";
                        $value = $result_arr[$virtual_disk_name]['AverageReadTime'];
                        print "{$virtual_disk}!{$value}\n";
                    }
                    break;
                case 'averageReadTimeServer2':
                    foreach ($virtual_disks as $virtual_disk){
                        $virtual_disk_name = "{$server2_IP}/{$virtual_disk}";
                        $value = $result_arr[$virtual_disk_name]['AverageReadTime'];
                        print "{$virtual_disk}!{$value}\n";
                    }
                    break;
                # --- Average write time ---
                case 'averageWriteTimeServer1':
                    foreach ($virtual_disks as $virtual_disk){
                        $virtual_disk_name = "{$server1_IP}/{$virtual_disk}";
                        $value = $result_arr[$virtual_disk_name]['AverageWriteTime'];
                        print "{$virtual_disk}!{$value}\n";
                    }
                    break;
                case 'averageWriteTimeServer2':
                    foreach ($virtual_disks as $virtual_disk){
                        $virtual_disk_name = "{$server2_IP}/{$virtual_disk}";
                        $value = $result_arr[$virtual_disk_name]['AverageWriteTime'];
                        print "{$virtual_disk}!{$value}\n";
                    }
                    break;
            }
        } 
        catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } 
        finally {
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
            
            $sql_command = 'SELECT * FROM '. $table;
            $result = $conn->query($sql_command);
            
            $result_arr = [];
            while ($row = $result->fetch_assoc()){
                $result_arr[$row['ip_name']] = $row;                    
            }
            switch ($arg){
                case 'index':
                    return $index;
                    break;
                # --- Desr ---
                case 'server1Desr':
                    return $server1_IP;
                    break;
                case 'server2Desr':
                    return $server2_IP;
                    break;
                # --- Average read time ---
                case 'averageReadTimeServer1':
                    $virtual_disk_name = "{$server1_IP}/{$index}";
                    return $result_arr[$virtual_disk_name]['AverageReadTime'];                    
                    break;
                case 'averageReadTimeServer2':
                    $virtual_disk_name = "{$server2_IP}/{$index}";
                    return $result_arr[$virtual_disk_name]['AverageReadTime'];                    
                    break;
                # --- Average write time ---
                case 'averageWriteTimeServer1':
                    $virtual_disk_name = "{$server1_IP}/{$index}";
                    return $result_arr[$virtual_disk_name]['AverageWriteTime'];                    
                    break;
                case 'averageWriteTimeServer2':
                    $virtual_disk_name = "{$server2_IP}/{$index}";
                    return $result_arr[$virtual_disk_name]['AverageWriteTime'];                    
                    break;
            }
        } catch (Exception $e) {
            # 處理異常
            die("Error linking database: " . $conn->connect_error);
        } finally {
            # 釋放連線
            $conn->close();
        }
    }
}
