import mysql.connector, time



# 將游標中的輸出訊息全部打印出來
def print_cursor(cursor):
    tables = cursor.fetchall()
    for table in tables:
        print(table)

def MySQL_connection_testing(setting, detail=True):
    with mysql.connector.connect(**setting) as connector:
        cursor = connector.cursor()
        cursor.execute("USE {};".format(setting["database"]))
        cursor.execute("SHOW TABLES;")
        if detail:
            print("MySQL帳號登入成功,資料表檢查成功")



def adjust_database(MYSQL_SETTING, TABLE_NAME, TABLE_PRIMARY_KEY, item_list):
    global ping_queue, lock
    with mysql.connector.connect(**MYSQL_SETTING) as connector:
        cursor = connector.cursor()

        # 檢查DB監測對象是否跟config相同(雙向檢查) 
        cursor.execute("SELECT * FROM {};".format(TABLE_NAME))
        db_item_list = []
        record = ''
        for row in cursor.fetchall():
            db_item = row[0]
            if db_item not in item_list:
                SQL_command = "DELETE from {} where {}='{}';".format(TABLE_NAME, TABLE_PRIMARY_KEY, db_item)
                record += '{}\n'.format(SQL_command)
                cursor.execute(SQL_command)
                continue
            db_item_list.append(db_item)

        for item in item_list:
            if item not in db_item_list:
                SQL_command = "INSERT INTO {} ({}) VALUES ('{}');".format(TABLE_NAME, TABLE_PRIMARY_KEY, item)
                record += '{}\n'.format(SQL_command)
                cursor.execute(SQL_command)
        connector.commit()
        cursor.close()
    return record
        