from flask import *
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
import mysql.connector
from flask.json import jsonify
from flask import Flask, request, abort,jsonify
from flask import Flask, abort
from flask import Flask
from flask import Flask, jsonify
from flask_cors import CORS
from flaskext.mysql import MySQL

from flask_restful import Resource, Api #for RESTful

# ------------------------------------MySQL 連線
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="88888888",# 上傳為Ff88888888   本地為88888888
    auth_plugin='mysql_native_password', # For EC2
    db="website",
    charset="utf8",
)
mycursor = mydb.cursor(dictionary=True)

app = Flask(__name__,   static_folder="static",
            static_url_path="/")
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app)

api = Api(app)#for RESTful

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
       keyword,nextpagecount,)  # 下一頁的DATA for KEYWOR 判斷null 用的 
    

    
    try:# error 處理
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
                myresult[x].update(imagestolist) # 一個一個加上去
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
            b = [None , myresult]  # None 才會顯示 null
            myresult_nextPage_null = dict(zip(a, b))
            print(myresult_nextPage_null["nextPage"])
            print(type(myresult_nextPage_null["nextPage"]))

            return myresult_nextPage_null
        return myresult_dict_from_list          
    except : 
        return abort(500)

# 網址代參數  旅遊景點 第二個API

@app.route("/api/attraction/<id>")
       
def attractionid(id):
    
    try:# error 處理
        # id= request.args.get("id")
        sql_id = "SELECT id,name,category,description,address,transport,mrt,latitude,longitude,images FROM attration20 WHERE id=%s ; " % (
            id,)
        mycursor.execute(sql_id)
        myresult = mycursor.fetchall() 
        list_image=myresult[0]["images"].split(",")# 變成列表
        list_image=list_image[0:-1]# 扣掉最後一筆LIST 因為是空的

        c=["images"]
        d=[list_image]
        imagestolist=dict(zip(c, d)) # 黏回去
        myresult[0].update(imagestolist)

        a = ["data"]
        b = myresult  # 變成不是list 
        myresult_dict_from_list = dict(zip(a, b))
        return myresult_dict_from_list

# error 處理
    except id=="" or id =="id"or id ==None: 
        return abort(404)
    except  : 
        return abort(500)

@app.errorhandler(500)
def handle_bad_request(e):
    return jsonify({ "error": True, "message": "伺服器內部錯誤"}), 500 #from flask import Flask, jsonify 可以直接寫字典格式出來
    

@app.errorhandler(404)
def handle_bad_request(e):
    return jsonify({ "error": True, "message":"景點編號不正確"}), 400 #後面可以自訂HTTP STATUS 數字
    







# ---------------------------------------------

# 用RESTful API 才能有同一個接口
# 使用者 第一個API

@app.route("/api/user") 
def members():#GET 方法
    email = request.args.get("email")
    emailsql = "SELECT id,name,email FROM member WHERE email='%s'" % (email,)
    mycursor.execute(emailsql)
    emailresult = mycursor.fetchone()
    if emailresult == None:
        return "{\"data\":null}"
    return json.dumps(emailresult, ensure_ascii=False)






# 使用者 第2個API
@app.route("/signup",methods=["POST"])
def signup():
    nickname=request.form["nickname"]
    username=request.form["usernameup"]
    password=request.form["passwordup"]
    sql = "SELECT 'name','username','password' FROM member WHERE username =%s"
    user =(username,)
    mycursor.execute(sql,user)
    myresult = mycursor.fetchone() 
    if  myresult != None :
        return redirect("http://127.0.0.1:3000/error?message=帳號已經被註冊")
    elif nickname   =="":
        return redirect("http://127.0.0.1:3000/error?message=姓名、帳號、密碼不能為空白")
    elif username   =="":
        return redirect("http://127.0.0.1:3000/error?message=姓名、帳號、密碼不能為空白")
    elif password   =="":
        return redirect("http://127.0.0.1:3000/error?message=姓名、帳號、密碼不能為空白")

    sql = "INSERT INTO member (name,username,password) VALUES (%s, %s, %s)"
    val = (nickname, username, password)
    mycursor.execute(sql, val)
    mydb.commit()
    return redirect("http://127.0.0.1:3000/")


# 使用者 第3個API 要用PATCH
@app.route("/signin", methods=["POST"])
def signin():
    username=request.form["username"]
    password=request.form["password"]
    sql = "SELECT * FROM member WHERE username='%s' and password='%s'" %(username,password)
    mycursor.execute(sql)
    myresult = mycursor.fetchone() 
    if myresult == None:
        return redirect("http://127.0.0.1:3000/error?message=帳號、或密碼輸入錯誤")
    session["nickname"]=myresult['name'] 
    return redirect("http://127.0.0.1:3000/member")






# 使用者 第4個API 要用DELETE

@app.route("/signout")
def signout():
    del session["nickname"]
    return redirect("http://127.0.0.1:3000/")





# ---------------------------------------------

#Create an instance of MySQL
mysql = MySQL()

#Set database credentials in config.
app.config['MYSQL_DATABASE_USER'] = 'user_name'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'database_name'
app.config['MYSQL_DATABASE_HOST'] = 'server_name'


          
#Get a user by id, update or delete user
class User(Resource):
    def get(self, user_id):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('select * from otg_demo_users where id = %s',user_id)
            rows = cursor.fetchall()
            return jsonify(rows)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

    def put(self, user_id):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            _name = request.form['name']
            _age = request.form['age']
            _city = request.form['city']
            update_user_cmd = """update otg_demo_users 
                                 set name=%s, age=%s, city=%s
                                 where id=%s"""
            cursor.execute(update_user_cmd, (_name, _age, _city, user_id))
            conn.commit()
            response = jsonify('User updated successfully.')
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify('Failed to update user.')         
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()    
            return(response)       

    def delete(self, user_id):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('delete from otg_demo_users where id = %s',user_id)
            conn.commit()
            response = jsonify('User deleted successfully.')
            response.status_code = 200
        except Exception as e:
            print(e)
            response = jsonify('Failed to delete user.')         
            response.status_code = 400
        finally:
            cursor.close()
            conn.close()    
            return(response)       



#API resource routes
# api.add_resource(UserList, '/users', endpoint='users')
api.add_resource(User, '/user/<int:user_id>', endpoint='user')


if __name__ == "__main__":
app.run(host='0.0.0.0', port=3000) (debug=True)
