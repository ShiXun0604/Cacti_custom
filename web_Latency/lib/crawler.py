import requests, time, urllib3



# 如果關鍵字在裡面則寫入時間差
# 禁用SSL驗證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全域儲存結果的地方
global Latency
Latency = {}

def Monit(KeyWD, url, timeout):
    global Latency
     # 將delay時間抓出來存入Latency
    start_time = time.time()
    r_chunk = ''
    with requests.get(url, stream=True, verify=False, timeout=timeout) as r:
        # 用stream方式遞迴抓取網頁
        for chunk in r.iter_content(chunk_size=512, decode_unicode=True):
            # 偵測關鍵字是否在裡面
            if KeyWD in r_chunk+chunk:
                Latency[url] = (time.time() - start_time)*1000
                break
            else:
                r_chunk = chunk
        else:
            Latency[url] = 240
            raise TypeError("URL contains no keyword.")