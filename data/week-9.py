import mysql.connector
import json

json_data = open("C:\\Users\\JAY\\Desktop\\tmp\\taipei-day-trip-website\\data\\taipei-attractions.json",
                 'r',  encoding='utf-8-sig').read()  # .read() 解決cp950
json_obj = json.loads(json_data)
rawdata = json_obj["result"]["results"]
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Ff88888888",# For EC2
    auth_plugin='mysql_native_password', # For EC2
    db="website",
    charset="utf8",
)
mycursor = mydb.cursor()
for item in rawdata:
    num = item["_id"]
    name = item["stitle"]
    category = item["CAT2"]
    description = item["xbody"]
    address = item["address"]
    transport = item["info"]
    mrt = item["MRT"]
    latitude = item["latitude"]
    longitude = item["longitude"]
    raw1 = item["file"].casefold().split(".jpg")  # 每個景點 [0~n]切成list
    strjpg = ""
    listjpg = []
    for i in range(len(raw1)-1):
        if raw1[i].endswith('.mp3') or raw1[i].endswith('.flv') == False:
            rawjpg = raw1[i]+".jpg"  # str
        strjpg = rawjpg+","+strjpg
        listjpg.append(rawjpg)
    images = strjpg  # 輸入string to MYSQL
    try:  # 解決 :  _mysql_connector.MySQLInterfaceError: Column 'mrt' cannot be null
        sql = "INSERT INTO attration20 (num,name,category,description,address,transport,mrt,latitude,longitude,images) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # 要加逗號!!!!! 解決 :   mysql.connector.errors.ProgrammingError: Could not process parameters: str(新北投溫泉區), it must be of type list, tuple or dict
        val = (num, name, category, description, address,transport, mrt, latitude, longitude, images,)
        mycursor.execute(sql, val)
        mydb.commit()  # mysql.connector.errors.DatabaseError: 1364 (HY000): Field 'category' doesn't have a default value  >>解決 :  https://stackoverflow.com/questions/15438840/mysql-error-1364-field-doesnt-have-a-default-values
    except:
        pass
