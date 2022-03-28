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
mycursor = mydb.cursor(dictionary=True)

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
            print(myresult_nextPage_null["nextPage"])
            print(type(myresult_nextPage_null["nextPage"]))

            return myresult_nextPage_null
        return myresult_dict_from_list
    except:
        return abort(500)

# 網址代參數  旅遊景點 第二個API


@app.route("/api/attraction/<id>")
def attractionid(id):

    try:  # error 處理
        # id= request.args.get("id")
        sql_id = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 WHERE id=%s ; " % (
            id,)
        mycursor.execute(sql_id)
        myresult = mycursor.fetchall()
        if myresult == None or id == "" or id == "id" or id == None:

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
            print("有嗎", "email")
            sql = "SELECT id,name,email FROM member WHERE email='%s'" % (
                email,)
            mycursor.execute(sql)
            myresult = mycursor.fetchone()
            print(myresult)
            myresult2 = json.dumps(myresult, ensure_ascii=False)
            myresult3 = "{\"data\":"+myresult2+"}"
            print(myresult3)
            return myresult3

        return "{\"data\":null}"

# 使用者 第2個API POST

    elif request.method == 'POST':
        try:
            name = request.form["registeruser"]
            email = request.form["registeremail"]
            print("email", email, type(email))
            password = request.form["registerrepassword"]
            print("註冊", name, email, password)
            sql = "SELECT 'name','email','password' FROM member WHERE email =%s"
            emailtuple = (email,)  # 變TUPLE
            print("註冊", name, email, password)
            mycursor.execute(sql, emailtuple)
            print("mycursor", mycursor)
            myresult = mycursor.fetchone()
            print("註冊signupresult  myresult", myresult)
            if myresult != None:
                return jsonify({"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}), 400
            elif name == "" or email == "" or password == "":
                return jsonify({"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}), 400
            sql = "INSERT INTO member (name,email,password) VALUES (%s, %s, %s)"
            val = (name, email, password)
            print("val", val)
            mycursor.execute(sql, val)
            mydb.commit()
            return jsonify({"ok": True}), 200

        except:
            return abort(500)


# 使用者 第3個API PATCH

    elif request.method == 'PATCH':

        try:
            email = request.form["email"]
            print("email ?", email,)
            password = request.form["password"]
            print("password ?", password)
            sql = "SELECT * FROM member WHERE email='%s' and password='%s'" % (
                email, password)
            mycursor.execute(sql)
            # global emailresult
            myresult = mycursor.fetchone()
            print(myresult)

            if myresult == None:
                session["email"] = None
                session.clear()
                return jsonify({"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"}), 400

            session["email"] = email
            print("存入session", session["email"])
            return jsonify({"ok": True})

        except:
            return abort(500)

 # 使用者 第4個API 要用DELETE

    elif request.method == 'DELETE':
        del session["email"]
        session.clear()

        return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
