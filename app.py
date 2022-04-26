import os
from datetime import date
from flask import *
from flask import Flask
from flask import request
import requests
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
from flask_restful import Resource, Api  # for RESTful
import mysql.connector.pooling
from mysql.connector import pooling
import re
from dotenv import load_dotenv
load_dotenv()


# ------------------------------------MySQL 連線


mydb_con = pooling.MySQLConnectionPool(pool_name="mysql_native__pool",
                                       pool_size=10,
                                       host="127.0.0.1",  # SQL的
                                       auth_plugin='mysql_native_password',  # For EC2
                                       user="root",
                                       charset="utf8",
                                       db="website",
                                       password=os.getenv("password"),)


app = Flask(__name__,   static_folder="static",
            static_url_path="/")

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


@app.route("/member")
def member():
    return render_template("member.html")


# 旅遊景點 第一個API

@app.route("/api/attractions")
def attractions():
    page = request.args.get("page", 0)  # 讀取頁數
    page = int(page)  # 轉換為整數形式
    pagecount = page*12  # 頁數變成INT *12
    nextpagecount = (page+1)*12
    try:  # error 處理
        mydb = mydb_con.get_connection()
        mycursor = mydb.cursor(dictionary=True, buffered=True)

        keyword = request.args.get("keyword")  # 建立關鍵字搜尋
        sqlkeyword = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 WHERE name LIKE '%%%s%%' LIMIT %s,12; " % (
            keyword, pagecount,)  # 建立關鍵字搜尋test

        sql1 = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 LIMIT %s,12; " % (
            pagecount,)

        sqlnextpage = "SELECT name FROM attration20 LIMIT %s,12; " % (
            nextpagecount,)  # 下一頁的DATA

        sqlkeywordnextpage = "SELECT name FROM attration20  WHERE name LIKE '%%%s%%'  LIMIT %s,12; " % (
            keyword, nextpagecount,)  # 下一頁的DATA for KEYWOR 判斷null 用的

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
    finally:
        mydb.close()


# 網址代參數  旅遊景點 第二個API


@app.route("/api/attraction/<id>")
def attractionid(id):

    try:

        mydb = mydb_con.get_connection()
        mycursor = mydb.cursor(dictionary=True, buffered=True)

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

    except:
        return abort(500)

    # finally:
    #     mydb.close()


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
            global mydb
            mydb = mydb_con.get_connection()
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            emailsql = "SELECT id,name,email,password FROM member WHERE email='%s'" % (
                email,)
            mycursor.execute(emailsql)
            myresult = mycursor.fetchone()
            # print(myresult)
            mydb.close()
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
            mydb = mydb_con.get_connection()
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            sql = "SELECT 'name','email','password' FROM member WHERE email =%s"
            emailtuple = (email,)  # 變TUPLE
            # print("註冊", name, email, password)
            mycursor.execute(sql, emailtuple)
            # print("mycursor", mycursor)
            myresult = mycursor.fetchone()
            # mydb.close()
            # print("註冊signupresult  myresult", myresult)
            pattern = re.compile("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")

            if myresult != None:
                return jsonify({"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}), 400
            elif name == "" or email == "" or password == "":
                return jsonify({"error": True, "message": "註冊失敗，未輸入正確姓名、信箱或密碼"}), 400
            elif pattern.findall(email) == []:
                return jsonify({"error": True, "message": "註冊失敗，未輸入正確信箱格式"}), 400
            sql = "INSERT INTO member (name,email,password) VALUES (%s, %s, %s)"
            val = (name, email, password)
            # print("val", val)
            mycursor.execute(sql, val)
            mydb.commit()
            return jsonify({"ok": True}), 200

        except:
            return abort(500)
        finally:
            mydb.close()

# 使用者 第3個API PATCH

    elif request.method == 'PATCH':

        try:
            mydb = mydb_con.get_connection()
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            email = request.form["email"]
            password = request.form["password"]
            sql = "SELECT * FROM member WHERE email='%s' and password='%s'" % (
                email, password)
            mycursor.execute(sql)
            myresult = mycursor.fetchone()

            if myresult == None:
                session["email"] = None
                session.clear()
                return jsonify({"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"}), 400

            session["email"] = email
            # print("存入session", session["email"])
            return jsonify({"ok": True})

        except:
            return abort(500)
        finally:
            mydb.close()

 # 使用者 第4個API 要用DELETE

    elif request.method == 'DELETE':
        del session["email"]
        session.clear()

        return jsonify({"ok": True})


@app.route("/api/edituser", methods=['POST'])
def editapiuser():
    # try:
    
    userdata = json.loads(request.get_data(as_text=True))
    print(userdata)
    userpassword = userdata['registerrepassword']
    useremail = userdata['registeremail']
    username = userdata['registeruser']
   
    email=session["email"]
    print("email", email)
   
        
    mydb = mydb_con.get_connection()
    mycursor = mydb.cursor(dictionary=True, buffered=True)
    sql = "SELECT * FROM member WHERE email =%s"
    emailtuple = (email,)  # 變TUPLE
    # print("註冊", name, email, password)
    mycursor.execute(sql, emailtuple)
    # print("mycursor", mycursor)
    myresult = mycursor.fetchone()
    # mydb.close()
    # print("註冊signupresult  myresult", myresult)
    pattern = re.compile("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")
    print("  myresult", myresult)
    print("myresult[name]", myresult["name"])
 
    if username == "" or useremail == "" or userpassword == "":
        mydb.close()
        return jsonify({"error": True, "message": "註冊失敗，未輸入正確姓名、信箱或密碼"}), 400
    elif pattern.findall(useremail) == []:
        mydb.close()
        return jsonify({"error": True, "message": "註冊失敗，未輸入正確信箱格式"}), 400
    # elif username == myresult["name"] and useremail ==myresult["email"] and userpassword  ==myresult["password"]:
    #     mydb.close()
    #     return jsonify({"error": True, "message": "未做修改"}), 400
    elif useremail != email :
        sql = "UPDATE member SET name=%s,email=%s,password=%s  WHERE email=%s"
        val = (username,  useremail, userpassword, email)
        mycursor.execute(sql, val)
        print("sql", val)
        mydb.commit()
        print("session[]",email)
        mydb.close()
 

        mydb = mydb_con.get_connection()
        mycursor = mydb.cursor(dictionary=True, buffered=True)
        ordersql = "UPDATE order2 SET memberEmail=%s  WHERE memberEmail=%s"
        orderval = (useremail, email)
        mycursor.execute(ordersql, orderval)
        print("ordersql", orderval)
        mydb.commit()
        mydb.close()

        session["email"]=useremail
        print("session[]",session["email"])
        email=session["email"]
        print("session[]",email)

        return jsonify({"ok": True}), 200
    elif useremail == email :
        sql = "UPDATE member SET name=%s,email=%s,password=%s  WHERE email=%s"
        val = (username,  useremail, userpassword, email)

        print("val", val)
        mycursor.execute(sql, val)
        mydb.commit()
    
        mydb.close()
        
        return jsonify({"ok": True}), 200

    # except:
    #     return abort(500)
    # finally:
    #     mydb.close()
# 階段二 WEEK 5 API


@app.route("/api/booking", methods=['GET', 'POST', 'DELETE'])
def apibookingg():

    if request.method == 'GET':

        if "email" in session:  # 登入成功
            mydb = mydb_con.get_connection()
            mycursor = mydb.cursor(dictionary=True, buffered=True)
            email = session["email"]

            sqlshoppingCart2 = "SELECT attractionId,date,time,price FROM shoppingCart2 WHERE email='%s'" % (
                email,)
            mycursor.execute(sqlshoppingCart2)
            myresult = mycursor.fetchone()
            attractionId = myresult["attractionId"]

            sqlattractionId = "SELECT id,name,address,images FROM attration20 WHERE id='%s'" % (
                attractionId,)
            mycursor.execute(sqlattractionId)
            attractionIdresult = mycursor.fetchall()
            list_image = attractionIdresult[0]["images"].split(",")  # 變成列表
            first_image = list_image[0]  # 只取第一筆 image
            c = ["image"]  # 沒有s 複數
            d = [first_image]
            imagestolist2 = dict(zip(c, d))  # 黏回去
            del attractionIdresult[0]["images"]
            attractionIdresult[0].update(imagestolist2)
            bookingResult1 = dict(zip(["attraction"], [attractionIdresult[0]]))
            bookingResult1.update(myresult)
            bookingResult = dict(zip(["data"], [bookingResult1]))

            mydb.close()
            return jsonify(bookingResult), 200
        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    elif request.method == 'DELETE':
        if "email" in session:  # 登入成功
            email = session["email"]
            mydb = mydb_con.get_connection()
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

        data = json.loads(request.get_data(as_text=True))

        if "email" in session:  # 登入成功

            if data['date'] == None or data['date'] == '':
                return jsonify({"error": True, "message": "未選取日期"})

            try:

                mydb = mydb_con.get_connection()
                mycursor = mydb.cursor(dictionary=True, buffered=True)

                attractionId = data['attractionId']
                date = data['date']
                time = data['time']
                price = data['price']
                email = session["email"]

                # print("1, " , date)
                # print("2, " , datetime.now().strftime("%Y-%m-%d"))
                # print("3, " , datetime.strptime(date, "%Y-%m-%d"))
                # print("4, " , datetime.strptime( datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"))
                if datetime.strptime(date, "%Y-%m-%d") >= datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"):
                    # print("4, " , datetime.strptime(date, "%Y-%m-%d") > datetime.strptime( datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"))
                    sqlchk = "SELECT attractionId,email  FROM shoppingCart2 WHERE email='%s'" % (
                        email,)

                    mycursor.execute(sqlchk)
                    sqlchkresult = mycursor.fetchone()

                    if sqlchkresult == [] or sqlchkresult == None:

                        sql = "INSERT INTO shoppingCart2 (date,email,time,price,attractionId) VALUES (%s, %s, %s, %s, %s)"
                        val = (date, email, time, price, attractionId)

                        mycursor.execute(sql, val)
                        mydb.commit()
                        mydb.close()
                    elif sqlchkresult != [] or sqlchkresult != None:

                        sqlupdate = "UPDATE shoppingCart2 SET date=%s,time=%s,price=%s,attractionId=%s  WHERE email=%s  "
                        val = (date,  time, price, attractionId, email)
                        mycursor.execute(sqlupdate, val)
                        mydb.commit()
                        mydb.close()
                    return jsonify({"ok": True}), 200
                return jsonify({"error": True, "message": "不能選取過去日期"}), 400

            except:
                return abort(500)

        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        else:  # 建立失敗，輸入不正確或其他原因
            return jsonify({"error": True, "message": "建立失敗，輸入不正確或其他原因"}), 400


# WEEK-6 串金流
@app.route("/api/orders", methods=['POST'])
def apiorders():
    try:
        mydb = mydb_con.get_connection()
        mycursor = mydb.cursor(dictionary=True, buffered=True)
        #  抓前端booking的資料 傳回前端
        if "email" in session:  # 登入成功
            memberEmail = session["email"]
            print(memberEmail)
            orderdata = json.loads(request.get_data(as_text=True))
            prime = orderdata['prime']
            price = orderdata['order']['price']
            email = orderdata['order']['contact']['email']
            phone = orderdata['order']['contact']['phone']
            contactName = orderdata['order']['contact']['name']
            date = orderdata['order']['trip']['date']
            time = orderdata['order']['trip']['time']
            address = orderdata['order']['trip']['attraction']['address']
            id = orderdata['order']['trip']['attraction']['id']
            image = orderdata['order']['trip']['attraction']['image']
            name = orderdata['order']['trip']['attraction']['name']
            status = 1

            number = str(datetime.now())
            number = datetime.strptime(number, '%Y-%m-%d %H:%M:%S.%f')
            number = number.strftime("%Y%m%d%H%M%S") + \
                str(random.randint(1000, 9999))
            number = str(number)
            patternemail = re.compile(
                "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")
            patternphone = re.compile(
                "(\d{2,3}-?|\(\d{2,3}\))\d{3,4}-?\d{4}|09\d{2}(\d{6}|-\d{3}-\d{3})")

            if email != "" and phone != "" and contactName != "" and patternemail.findall(email) != [] and patternphone.findall(phone) != []:

                # order 是 MYSQL 保留字
                sql = "INSERT INTO order2 (number,price,id,name,address,image,date,time,contactName,email,phone,status,memberEmail) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s, %s)"
                val = (number, price, id, name, address, image,
                       date, time, contactName, email, phone, status, memberEmail)

                mycursor.execute(sql, val)
                mydb.commit()

                # 對Tappay 發送請求
                #  Merchant ID  在商家設置    f789520_TAISHIN	  /  f789520_CTBC_Union_Pay    / f789520_CTBC
                # 帳號金鑰(Partner Key )在總覽項目:  partner_iwECA4RtFItOq1r9cpgHAzOvjGQSSnGf5LFkRZdNdTNT90GpkUE8qs1s

                # URL: https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime

                order_data = {

                    "prime": prime,
                    "partner_key": os.getenv("partner_key"),
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
                    'x-api-key': os.getenv("partner_key")
                }

                r = requests.post('https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime',
                                  data=json.dumps(order_data), headers=order_headers)

                payment_status = json.loads(
                    r.text)["status"]  # 付款狀態 0表示成功 1未付款
                rec_trade_id = json.loads(r.text)["rec_trade_id"]  # 付款紀錄編號

                if payment_status == 0:  # 如果付款成功
                    # 將訂單的狀態更新成0
                    print("付款成功", number)
                    order2sql = "UPDATE order2 SET status=%s WHERE number=%s  "
                    val = (0, number)
                    mycursor.execute(order2sql, val)
                    # print("val", val)
                    mydb.commit()
                    # 紀錄付款編號paymentId
                    paymentsql = "INSERT INTO payment (number,paymentId,status) VALUES (%s, %s, %s)"
                    val = (number, rec_trade_id, payment_status)
                    # print("val", val)
                    mycursor.execute(paymentsql, val)
                    mydb.commit()
                    # 在島到預定行程頁面時 ， 刪除預定行程

                    return jsonify({"data": {"number": str(number), "payment": {"status": 0, "message": "付款成功"}}}), 200
                else:
                    return jsonify({"error": True, "message": "訂單建立失敗，輸入不正確或其他原因"}), 400
            else:

                return jsonify({"error": True, "message": "聯絡資訊輸入錯誤"}), 400
        elif "email" not in session:  # 沒登入
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    except:  # 伺服器內部錯誤

        return abort(500)
    finally:
        # if mydb.in_transaction:
        # mydb.roolback()
        mydb.close()


@app.route("/api/order/<orderNumber>", methods=['GET'])
def apiorderNumber(orderNumber):

    print(orderNumber)

    try:  # error 處理
        mydb = mydb_con.get_connection()
        mycursor = mydb.cursor(dictionary=True, buffered=True)

        if "email" in session:  # 登入成功

            # orderNumber= request.args.get("number")
            orderNumber = "SELECT  number,price,id,name,address,image,date,time,contactName,email,phone,status FROM order2 WHERE number=%s ; " % (
                orderNumber,)
            mycursor.execute(orderNumber)
            myresult = mycursor.fetchone()
            print("myresult", myresult)
            # mydb.close()

            if myresult == None or myresult == "":  # 沒訂單資料
                print("沒 訂單資料", myresult)
                return jsonify({"error": True, "message": "無此訂單資料"}), 400

            elif myresult != None or myresult != "":  # 有訂單資料
                print("有訂單資料", myresult)
                number = myresult["number"]
                # print("number",number)
                price = myresult["price"]
                id = myresult["id"]
                name = myresult["name"]
                address = myresult["address"]
                image = myresult["image"]
                date = myresult["date"]
                time = myresult["time"]
                contactName = myresult["contactName"]
                email = myresult["email"]
                phone = myresult["phone"]
                status = myresult["status"]

                return jsonify({"data": {"number": number,
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

    except:
        return abort(500)

    finally:
        # if mydb.in_transaction:
        #     mydb.roolback()
        mydb.close()


@app.route("/api/history", methods=['GET'])
def apihistory():
    try:  # error 處理
            mydb = mydb_con.get_connection()
            mycursor = mydb.cursor(dictionary=True, buffered=True)

            if "email" in session:  # 登入成功
                
                memberEmail = session["email"]
                print("memberEmail", memberEmail)
                sqlhistory = "SELECT  number,price,id,name,address,image,date,time,contactName,email,phone,status FROM order2  WHERE memberEmail='%s' ; " % (
                    memberEmail,)
                mycursor.execute(sqlhistory)
                myresult = mycursor.fetchall()
                print("myresult", myresult)
                print("myresult", str(myresult[0]["number"]))

                return jsonify(myresult), 200

            elif "email" not in session:  # 沒登入
                return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

    except:
        return abort(500)

    finally:
    
        mydb.close()    


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
