from datetime import date
from flask import *
from flask import Flask
from flask import request
import requests
# # import urllib
# # from collections import Mapping
# try:
#     from collections.abc import Mapping
# except ImportError:
#     from collections import Mapping
# # from typing import Mapping
# # import urllib3
# from collections.abc import Mapping, MutableMapping
from flask import render_template
from flask import redirect
import mysql.connector
from flask.json import jsonify
from flask import Flask, request, abort, jsonify
from flask import Flask, abort
from flask import Flask
from flask import Flask, jsonify
from flask_cors import CORS
from flask import session
import time
from datetime import datetime, date
import random
# from flaskext.mysql import MySQL

from flask_restful import Resource, Api  # for RESTful

# ------------------------------------MySQL 連線
mydb = mysql.connector.connect(
    host="127.0.0.1",  # SQL的
    user="root",
    password="Ff88888888",
    auth_plugin='mysql_native_password',  # For EC2
    db="website",
    charset="utf8",

)
# 出现Unread result found解决 buffered=True
mycursor = mydb.cursor(dictionary=True, buffered=True)

app = Flask(__name__,   static_folder="static",
            static_url_path="/")
# app.config["JSON_AS_ASCII"] = False
# app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app)
app.secret_key = "test"  # for session

api = Api(app)  # for RESTful

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# 旅遊景點 第一個API

@app.route("/api/attractions")
def attractions():
    page = request.args.get("page", 0)  # 讀取頁數
    page = int(page)  # 轉換為整數形式
    pagecount = page*12  # 頁數變成INT *12
    nextpagecount = (page+1)*12

    keyword = request.args.get("keyword")  # 建立關鍵字搜尋
    sqlkeyword = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 WHERE name LIKE '%%%s%%' LIMIT %s,12; " % (
        keyword, pagecount,)  # 建立關鍵字搜尋test

    sql1 = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 LIMIT %s,12; " % (
        pagecount,)

    sqlnextpage = "SELECT name FROM attration20 LIMIT %s,12; " % (
        nextpagecount,)  # 下一頁的DATA

    sqlkeywordnextpage = "SELECT name FROM attration20  WHERE name LIKE '%%%s%%'  LIMIT %s,12; " % (
        keyword, nextpagecount,)  # 下一頁的DATA for KEYWOR 判斷null 用的

    try:  # error 處理
        # 判斷KEYWORD的地方，如果有 執行以下KEYWORD 流程
        if keyword != None:  # 如果有關鍵字的話執行關鍵字並呈現出來
            mycursor.execute(sqlkeyword)
            myresult = mycursor.fetchall()  # (dictionary=True 可變成字典

            # ----------image 處理變成迴圈
            for x in range(len(myresult)):
                mycursor.execute(sqlkeyword)
                sqlimage_myresult = mycursor.fetchall()
                list_image = sqlimage_myresult[x]["images"].split(",")  # 變成列表
                list_image = list_image[0:-1]  # 扣掉最後一筆LIST 因為是空的
                c = ["images"]
                d = [list_image]
                imagestolist = dict(zip(c, d))  # 黏回去
                myresult[x].update(imagestolist)  # 一個一個加上去
            a = ["nextPage", "data"]
            b = [page+1, myresult]  # 動態改下一頁
            myresult_dict_from_list = dict(zip(a, b))  # 兩個list 連在一起

            mycursor.execute(sqlkeywordnextpage)
            sqlnextpage_myresult = mycursor.fetchall()

            if sqlnextpage_myresult == []:  # 要擷取下一頁的資料判斷 ， 如果LIST為空[] 則變為null
                a = ["nextPage", "data"]
                b = [None, myresult]
                myresult_nextPage_null = dict(zip(a, b))
                return myresult_nextPage_null
            return myresult_dict_from_list

        mycursor.execute(sql1)
        myresult = mycursor.fetchall()  # (dictionary=True 可變成字典

        for x in range(len(myresult)):
            mycursor.execute(sql1)
            sqlimage_myresult = mycursor.fetchall()
            list_image = sqlimage_myresult[x]["images"].split(",")  # 變成列表
            list_image = list_image[0:-1]  # 扣掉最後一筆LIST 因為是空的
            c = ["images"]
            d = [list_image]
            imagestolist = dict(zip(c, d))  # 黏回去
            myresult[x].update(imagestolist)

        # ----------"nextPage", "data" 與資料庫結合
        a = ["nextPage", "data"]
        b = [page+1, myresult]  # 動態改下一頁
        myresult_dict_from_list = dict(zip(a, b))  # 兩個list 連在一起

        # ----------下一頁判斷
        mycursor.execute(sqlnextpage)
        sqlnextpage_myresult = mycursor.fetchall()

        if sqlnextpage_myresult == []:  # 要擷取下一頁的資料判斷 ， 如果LIST為空[] 則變為null
            a = ["nextPage", "data"]
            b = [None, myresult]  # None 才會顯示 null
            myresult_nextPage_null = dict(zip(a, b))
            # print(myresult_nextPage_null["nextPage"])
            # print(type(myresult_nextPage_null["nextPage"]))

            return myresult_nextPage_null
        return myresult_dict_from_list
    except:
        return abort(500)

# 網址代參數  旅遊景點 第二個API


@app.route("/api/attraction/<id>")
def attractionid(id):
    mydb = mysql.connector.connect(
        host="127.0.0.1",  # SQL的
        user="root",
        password="Ff88888888",
        auth_plugin='mysql_native_password',  # For EC2
        db="website",
        charset="utf8",

    )
    mycursor = mydb.cursor(dictionary=True, buffered=True)

    try:  # error 處理
        # id= request.args.get("id")
        sql_id = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 WHERE id=%s ; " % (
            id,)
        mycursor.execute(sql_id)
        myresult = mycursor.fetchall()
        mydb.close()
        if myresult == None or id == "" or id == "id" or id == None or myresult == "":

            return jsonify({"error": True, "message": "景點編號不正確"}), 400

        list_image = myresult[0]["images"].split(",")  # 變成列表
        list_image = list_image[0:-1]  # 扣掉最後一筆LIST 因為是空的

        c = ["images"]
        d = [list_image]
        imagestolist = dict(zip(c, d))  # 黏回去
        myresult[0].update(imagestolist)

        a = ["data"]
        b = myresult  # 變成不是list
        myresult_dict_from_list = dict(zip(a, b))

        return myresult_dict_from_list
# error 處理

    except:
        return abort(500)


@app.errorhandler(404)
def handle_bad_request(e):
    # from flask import Flask, jsonify 可以直接寫字典格式出來
    return jsonify({"error": True, "message": "景點編號不正確"}), 400


@app.errorhandler(500)
def handle_bad_request(e):
    # from flask import Flask, jsonify 可以直接寫字典格式出來
    return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500


# 階段二 WEEK 4 API
@app.route("/api/user", methods=['GET', 'POST', 'PATCH', 'DELETE'])
def apiuser():

    # 使用者 第1個API GET

    if request.method == 'GET':

        if "email" in session:
            email = session["email"]
            # print("有嗎", "email")
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            emailsql = "SELECT id,name,email FROM member WHERE email='%s'" % (
                email,)
            mycursor.execute(emailsql)
            myresult = mycursor.fetchone()
            # print(myresult)
            # mydb.close()
            myresult2 = json.dumps(myresult, ensure_ascii=False)
            myresult3 = "{\"data\":"+myresult2+"}"
            # print(myresult3)
            return myresult3

        return "{\"data\":null}"

# 使用者 第2個API POST 註冊

    elif request.method == 'POST':
        try:

            name = request.form["registeruser"]
            email = request.form["registeremail"]
            # print("email", email, type(email))
            password = request.form["registerrepassword"]
            # print("註冊", name, email, password)
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            sql = "SELECT 'name','email','password' FROM member WHERE email =%s"
            emailtuple = (email,)  # 變TUPLE
            # print("註冊", name, email, password)
            mycursor.execute(sql, emailtuple)
            # print("mycursor", mycursor)
            myresult = mycursor.fetchone()
            # mydb.close()
            # print("註冊signupresult  myresult", myresult)
            if myresult != None:
                return jsonify({"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}), 400
            elif name == "" or email == "" or password == "":
                return jsonify({"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}), 400
            sql = "INSERT INTO member (name,email,password) VALUES (%s, %s, %s)"
            val = (name, email, password)
            # print("val", val)
            mycursor.execute(sql, val)
            mydb.commit()
            return jsonify({"ok": True}), 200

        except:
            return abort(500)


# 使用者 第3個API PATCH

    elif request.method == 'PATCH':

        try:
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            email = request.form["email"]
            # print("email ?", email,)
            password = request.form["password"]
            # print("password ?", password)

            sql = "SELECT * FROM member WHERE email='%s' and password='%s'" % (
                email, password)
            mycursor.execute(sql)
            # global emailresult
            myresult = mycursor.fetchone()
            # mydb.close()
            # print(myresult)

            if myresult == None:
                session["email"] = None
                session.clear()
                return jsonify({"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"}), 400

            session["email"] = email
            # print("存入session", session["email"])
            return jsonify({"ok": True})

        except:
            return abort(500)

 # 使用者 第4個API 要用DELETE

    elif request.method == 'DELETE':
        del session["email"]
        session.clear()

        return jsonify({"ok": True})


# 階段二 WEEK 5 API


@app.route("/api/booking", methods=['GET', 'POST', 'DELETE'])
def apibookingg():
    mydb = mysql.connector.connect(
        host="127.0.0.1",  # SQL的
        user="root",
        password="Ff88888888",
        auth_plugin='mysql_native_password',  # For EC2
        db="website",
        charset="utf8",

    )
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    if request.method == 'GET':

        if "email" in session:  # 登入成功
            email = session["email"]
            # print("session[ ]", email)  # session[ ] ply@ply.com
            mycursor = mydb.cursor(dictionary=True, buffered=True)

            sqlshoppingCart2 = "SELECT attractionId,date,time,price FROM shoppingCart2 WHERE email='%s'" % (
                email,)
            mycursor.execute(sqlshoppingCart2)
            myresult = mycursor.fetchone()
            # mydb.close()

            # myresult {'attractionId': 9, 'date': '2022-03-29', 'time': 'afternoon', 'price': 2000}
            # print("myresult", myresult)
            # print("myresultTYPE", type(myresult))  # <class 'dict'>
            # myresult2 = json.dumps(myresult, ensure_ascii=False)
            # print("myresult2",myresult2) #myresult2 {"attractionId": 9, "date": "2022-03-29", "price": 2000, "time": "afternoon"}
            # print("myresult2TYPE",type(myresult2)) #<class 'str'>
            attractionId = myresult["attractionId"]
            # print("myresult2['attractionId']", myresult["attractionId"])  # 9

            mycursor = mydb.cursor(dictionary=True, buffered=True)
            sqlattractionId = "SELECT id,name,address,images FROM attration20 WHERE id='%s'" % (
                attractionId,)
            mycursor.execute(sqlattractionId)
            attractionIdresult = mycursor.fetchall()
            # mydb.close()
            # print("attractionIdresult", attractionIdresult)  # [{'id': 9, 'name': '地熱谷', 'address': '臺北市  北投區中山路', 'images': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c0/d37/e611/f805/ec29667c-0ff6-435a-ab82-2905492d04fc.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d988/e745/f29/cc1e0a3a-0e3c-47dc-88b8-9c7a9ddc606e.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d293/e834/f864/7493ca40-985e-4d7e-9340-f738b6096c26.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d375/e862/f67/dcada704-a151-4b49-ac44-a349e7761973.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d457/e341/f171/f6dc25a6-cc44-4e4d-a7ea-aea011e2aa65.jpg,https://www.travel.taipei/d_upload_ttn/sceneadmin/pic/11003993.jpg,'}]
            list_image = attractionIdresult[0]["images"].split(",")  # 變成列表
            first_image = list_image[0]  # 只取第一筆 image
            # https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg
            # print("first_image", first_image)
            c = ["image"]  # 沒有s 複數
            d = [first_image]
            imagestolist2 = dict(zip(c, d))  # 黏回去
            # {'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg'}
            # print("imagestolist", imagestolist2)
            # print(" attractionIdresult[0]", attractionIdresult[0])
            del attractionIdresult[0]["images"]
            # print("attractionIdresult[0]", attractionIdresult[0])
            # print("attractionIdresult[0]TYPE", type(attractionIdresult[0]))
            # print("imagestolistTYPE", type(imagestolist2))
            # print("imagestolist2", imagestolist2)
            attractionIdresult[0].update(imagestolist2)
            # attractionIdresult[0].update(imagestolist)
            # {'id': 9, 'name': '地熱谷', 'address': '臺北市  北投區中山路', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg'}
            # print(
            #     "attractionIdresult[0].update(imagestolist2)", attractionIdresult[0])

            bookingResult1 = dict(zip(["attraction"], [attractionIdresult[0]]))
            # bookingResult1="attraction"+ attractionIdresult[0]
            # {'attraction': {'id': 9, 'name': '地熱谷', 'address': '臺北市  北投區中山路', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg'}}
            # print("bookingResult1", bookingResult1)
            bookingResult1.update(myresult)
            bookingResult = dict(zip(["data"], [bookingResult1]))
            # {'data': {'attraction': {'id': 9, 'name': '地熱谷', 'address': '臺北市  北投區中山路', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/image/a0/b0/c1/d202/e23/f478/a219480b-2bb0-4e80-9069-2704c7904545.jpg'}, 'attractionId': 9, 'date': '2022-03-29', 'time': 'afternoon', 'price': 2000}}
            # print("bookingResult", bookingResult)

            mydb.close()
            return jsonify(bookingResult), 200
        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    elif request.method == 'DELETE':
        if "email" in session:  # 登入成功
            email = session["email"]
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            sqldelete = "DELETE FROM shoppingCart2 WHERE email='%s'" % (
                email,)
            mycursor.execute(sqldelete)
            mydb.commit()
            mydb.close()
            return jsonify({"ok": True}), 200
        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    elif request.method == 'POST':

        #  抓前端attration 的資料 傳回前端
        # try:
        data = json.loads(request.get_data(as_text=True))
        # print(data)

        # print(data['date'])

        if "email" in session:  # 登入成功
            if data['date'] == None or data['date'] == '':
                return jsonify({"error": True, "message": "未選取日期"})
            try:
                # print("進去 SQL 紀錄景點")
                attractionId = data['attractionId']
                date = data['date']
                time = data['time']
                price = data['price']
                email = session["email"]
                # print("進去 SQL 紀錄景點 LIST", attractionId,
                #       time, date, price, email)

                sqlchk = "SELECT attractionId,email  FROM shoppingCart2 WHERE email='%s'" % (
                    email,)
                mycursor = mydb.cursor(dictionary=True, buffered=True)
                mycursor.execute(sqlchk)
                sqlchkresult = mycursor.fetchone()
                # print("sqlchkresult", sqlchkresult)
                if sqlchkresult == [] or sqlchkresult == None:
                    # print("沒找到資料 用INSERT")

                    sql = "INSERT INTO shoppingCart2 (date,email,time,price,attractionId) VALUES (%s, %s, %s, %s, %s)"
                    val = (date, email, time, price, attractionId)
                    # print("val", val)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    # mydb.close()

                elif sqlchkresult != [] or sqlchkresult != None:
                    # print("找到資料 用 REPLACE")
                    # sql="SET SQL_SAFE_UPDATES=0;"
                    # mycursor.execute(sql)
                    # sql = "UPDATE shoppingCart2 SET date=date,time=time,price=price,attractionId=attractionId  WHERE email=email"
                    # mycursor.execute(sql)
                    sqlupdate = "UPDATE shoppingCart2 SET date=%s,time=%s,price=%s,attractionId=%s  WHERE email=%s  "
                    val = (date,  time, price, attractionId, email)
                    mycursor.execute(sqlupdate, val)
                    mydb.commit()

                    # sql="SET SQL_SAFE_UPDATES=1;"
                    mydb.close()

                return jsonify({"ok": True}), 200

            except:
                return abort(500)

            # return jsonify({"ok": True})
            # return jsonify(data)

        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        else:  # 建立失敗，輸入不正確或其他原因
            return jsonify({"error": True, "message": "建立失敗，輸入不正確或其他原因"}), 400

        # except: #伺服器內部錯誤

        #     return abort(500)


# 串金流
@app.route("/api/orders", methods=['POST'])
def apiorders():
    try:
        #  抓前端booking的資料 傳回前端
        if "email" in session:  # 登入成功
            orderdata = json.loads(request.get_data(as_text=True))
            print(orderdata)
            print(orderdata['prime'])
            print('price', orderdata['order']['price'])
            print('email', orderdata['order']['contact']['email'])
            print('phone', orderdata['order']['contact']['phone'])
            print('contactName', orderdata['order']['contact']['name'])
            print('date', orderdata['order']['trip']['date'])
            print('time', orderdata['order']['trip']['time'])
            print('address', orderdata['order']['trip']['attraction']['address'])
            print('id', orderdata['order']['trip']['attraction']['id'])
            print('image', orderdata['order']['trip']['attraction']['image'])
            print('name', orderdata['order']['trip']['attraction']['name'])
            prime = orderdata['prime']
            price = orderdata['order']['price']
            email = orderdata['order']['contact']['email']
            phone = orderdata['order']['contact']['phone']
            contactName = orderdata['order']['contact']['phone']
            date = orderdata['order']['trip']['date']
            time = orderdata['order']['trip']['time']
            address = orderdata['order']['trip']['attraction']['address']
            id = orderdata['order']['trip']['attraction']['id']
            image = orderdata['order']['trip']['attraction']['image']
            name = orderdata['order']['trip']['attraction']['name']
            status = 1

            mydb = mysql.connector.connect(
                host="127.0.0.1",  # SQL的
                user="root",
                password="Ff88888888",
                auth_plugin='mysql_native_password',  # For EC2
                db="website",
                charset="utf8",

            )
            mycursor = mydb.cursor(dictionary=True, buffered=True)

            # number =  time.strftime("%Y%m%d%H%M%S", time.localtime()) +str(random.randint(1000, 9999))  # 產生測試用自訂訂單編號
            # print('訂單',number)

            number = str(datetime.now())
            print(number)
            number = datetime.strptime(number, '%Y-%m-%d %H:%M:%S.%f')
            number = number.strftime("%Y%m%d%H%M%S")+str(random.randint(1000, 9999))
            print("number", number)
            number = int(number)
        # order 是 MYSQL 保留字
            sql = "INSERT INTO order2 (number,price,id,name,address,image,date,time,contactName,email,phone,status) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)"
            val = (number, price, id, name, address, image,
                date, time, contactName, email, phone, status)
            print("val", val)
            mycursor.execute(sql, val)
            mydb.commit()

            


        # 對Tappay 發送請求
        #  Merchant ID  在商家設置    f789520_TAISHIN	  /  f789520_CTBC_Union_Pay    / f789520_CTBC
        # 帳號金鑰(Partner Key )在總覽項目:  partner_iwECA4RtFItOq1r9cpgHAzOvjGQSSnGf5LFkRZdNdTNT90GpkUE8qs1s

        # URL: https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime

            order_data = {

                "prime": prime,
                "partner_key": "partner_iwECA4RtFItOq1r9cpgHAzOvjGQSSnGf5LFkRZdNdTNT90GpkUE8qs1s",
                "merchant_id": "f789520_CTBC",
                "details": "TapPay Test",
                "amount": 10000000,
                "cardholder": {
                    "phone_number": phone,
                    "name": contactName,
                    "email": email,  # "LittleMing@Wang.com"
                    "zip_code": "",
                    "address": address,
                    # "national_id": "A123456789"
                },
                "remember": True
            }

            order_headers = {
                'Content-Type': 'application/json',
                'x-api-key': "partner_iwECA4RtFItOq1r9cpgHAzOvjGQSSnGf5LFkRZdNdTNT90GpkUE8qs1s"
            }

            r = requests.post('https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime', data = json.dumps(order_data), headers=order_headers)




            print ("r.text",r.text)
            # print ("r.text TYPe",type(r.text))
            print ("r.text",json.loads(r.text))
            # print ("r.text TYPeTYPeTYPe",type(json.loads(r.text)))

            print (" json.loads(r.text)[status] ",json.loads(r.text)["status"], json.loads(r.text)["rec_trade_id"])
            # print ("r.raise_for_status()",r.raise_for_status())
            # print("r.status_code",r.status_code) 
            # print("r.content",r.content)
            # print("r.request",r.request)
            # print("r.ok",r.ok)
            # print("r.headers",r.headers)
            payment_status=json.loads(r.text)["status"] #付款狀態 0表示成功 1未付款
            rec_trade_id=json.loads(r.text)["rec_trade_id"] #付款紀錄編號

            
            if payment_status == 0: #如果付款成功
                #將訂單的狀態更新成0
                print ("付款成功",number  )
                order2sql = "UPDATE order2 SET status=%s WHERE number=%s  "
                val = (0,number)
                mycursor.execute(order2sql, val)
                # print("val", val)
                mydb.commit()
                #紀錄付款編號paymentId
                paymentsql = "INSERT INTO payment (number,paymentId,status) VALUES (%s, %s, %s)"
                val = (number,rec_trade_id,payment_status)
                # print("val", val)
                mycursor.execute(paymentsql, val)
                mydb.commit()
                #在島到預定行程頁面時 ， 刪除預定行程 


                # sql="SET SQL_SAFE_UPDATES=1;"
                mydb.close()
                
                return jsonify({"data": {"number": str(number),"payment": {"status": 0,"message": "付款成功"}}}), 200
            else: 
                return jsonify({"error": True, "message": "訂單建立失敗，輸入不正確或其他原因"}),400
        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    except: #伺服器內部錯誤
        return abort(500)




@app.route("/api/order/<orderNumber>", methods=['GET'])
def apiorderNumber(orderNumber):
    
    print(orderNumber)

    # try:  # error 處理
       

    if "email" in session:  # 登入成功
        mydb = mysql.connector.connect(
        host="127.0.0.1",  # SQL的
        user="root",
        password="Ff88888888",
        auth_plugin='mysql_native_password',  # For EC2
        db="website",
        charset="utf8",

        )
        mycursor = mydb.cursor(dictionary=True, buffered=True)

        # orderNumber= request.args.get("number")
        orderNumber = "SELECT  number,price,id,name,address,image,date,time,contactName,email,phone,status FROM order2 WHERE number=%s ; " % (
            orderNumber,)
        mycursor.execute(orderNumber)
        myresult = mycursor.fetchone()
        print("myresult",myresult)
        # mydb.close()

        if myresult == None  or myresult == "":#沒訂單資料
            print("沒 訂單資料",myresult)
            return jsonify({"error": True, "message": "無此訂單資料"}), 400

        elif myresult != None or myresult != "" : # 有訂單資料
            print("有訂單資料",myresult)
            number=myresult["number"]
            # print("number",number)
            price=myresult["price"]
            id=myresult["id"]
            name=myresult["name"]
            address=myresult["address"]
            image=myresult["image"]
            date=myresult["date"]
            time=myresult["time"]
            contactName=myresult["contactName"]
            email=myresult["email"]
            phone=myresult["phone"]
            status=myresult["status"]


            return jsonify({ "data": {"number": number,
                                "price": price,
                                "trip": {
                                "attraction": {
                                    "id": id,
                                    "name": name,
                                    "address": address,
                                    "image": image
                                },
                                "date": date,
                                "time": time
                                },
                                "contact": {
                                "name": contactName,
                                "email": email,
                                "phone": phone
                                },
                                "status": status
                            }}), 200

    elif "email" not in session:  # 沒登入
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
# error 處理

    # except:
    #     return abort(500)

    


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
