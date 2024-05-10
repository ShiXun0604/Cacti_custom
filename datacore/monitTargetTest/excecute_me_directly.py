import requests, urllib3, json
import xml.etree.ElementTree as ET



def output_all_monitor_objects(IP, AUTHORIZATION):
    headers = {
        'ServerHost': IP,
        'Authorization': AUTHORIZATION,
    }
    url = 'https://{ip}/RestService/rest.svc/1.0/monitors'.format(ip=IP)

    response = requests.get(url, headers=headers, verify=False).text
    data = json.loads(response)
    result = ''
    for object in data:
        for i in object.keys():
            result += '{:20}{}\n'.format(i, object[i])
        result += '---------------------------------------------\n'
    
    with open('AllMonitorObjects.txt', 'w') as f:
        f.write(result)

    return result

def output_difference_id(IP, AUTHORIZATION):
    headers = {
        'ServerHost': IP,
        'Authorization': AUTHORIZATION,
    }
    url = 'https://{ip}/RestService/rest.svc/1.0/monitors'.format(ip=IP)

    response = requests.get(url, headers=headers, verify=False).text
    data = json.loads(response)

    result_dict = {}
    for object in data:
        id = object['MonitoredObjectId']
        detail = object['ExtendedCaption']
        if id not in result_dict.keys():
            result_dict[id] = []
        result_dict[id].append(detail)
    
    result_string = ''
    for id in result_dict.keys():
        result_string += '{}\n'.format(id)
        for detail in result_dict[id]:
            result_string += '\t{}\n'.format(detail)
        result_string += '\n'

    with open('IdDetails.txt', 'w') as f:
        f.write(result_string)

    return result_string


# 禁用SSL驗證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Loads the config file
CONFIG_FILE_PATH = 'C:\cacti_expertos\datacore\Datacore_config.xml'
with open(CONFIG_FILE_PATH, 'rb') as f: 
    config = ET.fromstring(f.read().decode('utf-8'))

# API query server
QUERY_IP = config.find('APIqueryServer').find('IP').text
Authorization = config.find('APIqueryServer').find('Authorization').text

output_all_monitor_objects(QUERY_IP, Authorization)
output_difference_id(QUERY_IP, Authorization)
