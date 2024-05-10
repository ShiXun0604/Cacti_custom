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

# 禁用SSL驗證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Loads the config file
CONFIG_FILE_PATH = 'C:\cacti_expertos\datacore\Datacore_config.xml'
with open(CONFIG_FILE_PATH, 'rb') as f: 
    config = ET.fromstring(f.read().decode('utf-8'))

# API query server
QUERY_IP = config.find('APIqueryServer').find('IP').text
Authorization = 'Basic administrator 1qaz#EDC'

headers = {
    'ServerHost': QUERY_IP,
    'Authorization': Authorization,
}
id = 'V.{ac30d029-f7b7-11ee-81c8-005056846d92}-00000001_N.22250030D9067D76'
url = 'https://{ip}/RestService/rest.svc/1.0/performance/{id}'.format(ip=QUERY_IP, id=id)
#url = 'https://{ip}/RestService/rest.svc/1.0/monitors'.format(ip='10.5.5.82')

print(url)
response = requests.get(url, headers=headers, verify=False).text
if response[0] == '[':
    data = json.loads(response)
else:
    data = json.loads(response)
print(data)