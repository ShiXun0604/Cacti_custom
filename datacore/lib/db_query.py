import mysql.connector, time



# 將游標中的輸出訊息全部打印出來
def print_cursor(cursor):
    tables = cursor.fetchall()
    for table in tables:
        print(table)

# 測試cacti db可以連線
def DB_Conn_testing(setting, detail=False):
    with mysql.connector.connect(**setting) as connector:
        cursor = connector.cursor()
        cursor.execute("USE {};".format(setting["database"]))
        cursor.execute("SHOW TABLES;")
        if detail:
            print("MySQL帳號登入成功,資料表檢查成功")
            time.sleep(0.5)
        