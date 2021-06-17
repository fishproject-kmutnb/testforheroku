from flask import Flask ,flash, render_template ,request, jsonify,redirect,url_for , session ,g
import sqlite3
from passlib.hash import sha256_crypt
import numpy as np
import os
import random
import string
from flask_paginate import Pagination, get_page_args , get_page_parameter
app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = "/static/images"

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
################################################
@app.route("/dropsession")
def dropsession():
    session.pop('admin',None)
    print(session)
    session.clear()
    return redirect(url_for('gotoAdminpage'))
################################################
@app.route('/fish_document')
def shop_document():
    with sqlite3.connect("..\mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT * FROM seller"
        cur.execute(sql)
        result = cur.fetchall()
        return result

@app.route('/fishshop')
def fish_document():
    with sqlite3.connect("..\mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT * FROM fish_data"
        cur.execute(sql)
        result = cur.fetchall()
        print(len(result))
        return result

@app.route('/common_name')
def common_name_document():
    with sqlite3.connect("..\mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT * FROM common_name"
        cur.execute(sql)
        result = cur.fetchall()
        print(len(result))
        return result

@app.route("/insert_fish" )
def insert_fish(name,common_name):
    with sqlite3.connect("..\mydata.db") as connect:
        cur = connect.cursor()
        sql = "INSERT INTO fish_data (Name , Common_name) VALUES (?,?)"
        val = [name,common_name]
        cur.execute(sql,val)
        connect.commit()

        sql = "INSERT INTO common_name (Name , Common_name) VALUES (?,?)"
        val = [name,common_name]
        cur.execute(sql,val)
        connect.commit()

        return redirect(url_for('goto_fishpage'))

@app.route("/insert_shop")
def insert_shop(Seller_Name , Seller_Last , Address , Phone_Number , Email , shop_Name):
    with sqlite3.connect("..\mydata.db")as connect:
        cur = connect.cursor()
        password = str(get_random_string(6))
        print(password)
        sql = "INSERT INTO seller (Seller_Name , Seller_Last,Password , Address , Phone_Number , Email , shop_Name) VALUES (?,?, ?,?, ?,?, ?)"
        val = [Seller_Name , Seller_Last ,str(sha256_crypt.encrypt(password)), Address , Phone_Number , Email , shop_Name]
        cur.execute(sql,val)
        connect.commit()
    return redirect(url_for('goto_shoppage'))

@app.route("/save_fish")
def save_fish(No ,Name , Common_name , Feature , Feed , Aquarium):
    if session.get("admin",None) is not None:
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            sql = "UPDATE fish_data SET Name = ? , Common_name = ? , Feature = ? , Feed = ? , Aquarium = ? WHERE No = ?"
            val = [Name , Common_name , Feature , Feed , Aquarium,No]
            cur.execute(sql,val)
            connect.commit()
        return redirect(url_for('goto_fishpage'))
    # พืชน้ำและสัตว์น้ำขนาดเล็ก
@app.route("/save_shop")
def save_shop(Seller_Name , Seller_Last , Address , Phone_Number , Email , shop_Name):
    if session.get("admin",None) is not None:
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            sql = "UPDATE seller SET Seller_Name=? , Seller_Last=? , Address=? , Phone_Number=? , Email=? , shop_Name=? WHERE Email = ?"
            val = [Seller_Name,Seller_Last,Address,Phone_Number,Email,shop_Name,Email]
            cur.execute(sql,val)
            connect.commit()
        return redirect(url_for('goto_shoppage'))

@app.route("/update_status")
def update_status( seller_id,status_color):
    if session.get("admin",None) is not None:
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            status = ''
            print(status_color)
            if status_color == 'danger':
                status_color = 'secondary'
                status = 'เปิดร้านค้า'
            else:
                status_color = 'danger'
                status = 'ปิดร้านค้า'

            sql = "UPDATE seller SET seller_status_color = ? , seller_status = ? WHERE seller_ID = ?"
            val = [status_color , status , seller_id]
            cur.execute(sql,val)
            connect.commit()
        return redirect(url_for('goto_shoppage'))

################################################
@app.route("/update_shop", methods=["GET", "POST"])
def update_shop():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            Seller_Name = request.form.get("Seller_Name")
            Seller_Last = request.form.get("Seller_Last")
            Address = request.form.get("Address")
            Phone_Number = request.form.get("Phone_Number")
            Email = request.form.get("Email")
            shop_Name = request.form.get("shop_Name")
            return save_shop(Seller_Name , Seller_Last , Address , Phone_Number , Email , shop_Name)

@app.route("/add_shop", methods=["GET", "POST"])
def add_shop():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            Seller_Name = request.form.get("Seller_Name")
            Seller_Last = request.form.get("Seller_Last")
            Address = request.form.get("Address")
            Phone_Number = request.form.get("Phone_Number")
            Email = request.form.get("Email")
            shop_Name = request.form.get("shop_Name")
            return insert_shop(Seller_Name , Seller_Last , Address , Phone_Number , Email , shop_Name)

@app.route("/add_fish", methods=["GET", "POST"])
def add_fish():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            name = request.form.get("name")
            common_name = request.form.get("common_name")
            if request.files:
                file = request.files["image"]
                filepath = "static\\images\\pic_fish\\"+str(common_name)+".jpg"
                file.save(filepath)
                with sqlite3.connect("..\mydata.db") as connect:
                        cur = connect.cursor()
                        sql = "INSERT INTO fish_data (Name , Common_name , Feature, Feed, Aquarium) VALUES (?,?,?,?,?)"
                        val = [
                            name,
                            common_name,
                            'เพิ่มเติม',
                            'เพิ่มเติม',
                            'เพิ่มเติม'
                        ]
                        cur.execute(sql,val)
                        connect.commit()    

                        cur = connect.cursor()
                        sql = "INSERT INTO common_name (name , pic_fish) VALUES (?,?)"
                        val = [
                            common_name,
                            filepath
                        ]
                        cur.execute(sql,val)
                        connect.commit()  
                        return redirect(url_for('goto_fishpage'))

@app.route("/upload_model",methods=["GET", "POST"])
def upload_model():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            if request.files:
                model = "..\\"+"model"+".h5"
                file = request.files["model"]
                filepath = model
                file.save(filepath)
    return render_template("upload_model.html")

@app.route("/edit_fish", methods=["GET", "POST"])
def edit_fish():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            no = request.form.get("no")
            name=request.form.get("name")
            common_name=request.form.get("common_name")
            feature = request.form.get("feature")
            feed = request.form.get("feed")
            aquarium = request.form.get("aquarium")
            return save_fish(no,name , common_name , feature , feed , aquarium)

@app.route("/status_shop", methods=["GET", "POST"])
def status_shop():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            seller_id = request.form.get("seller_id")
            status_color = request.form.get("status_color")
            print(status_color)
            return update_status(seller_id,status_color)

@app.route("/search_common_name" , methods=["GET" , "POST"])
def search_common_name():
    if session.get("admin",None) is not None:
        if request.method=="POST":
            Fish_name = request.form['search_name']
            common_name_doc = common_name_document()
            with sqlite3.connect("..\mydata.db") as connect:
                cur = connect.cursor()

                sql = "SELECT * FROM common_name WHERE name LIKE ?"
                val = ['%'+Fish_name+'%']
                cur.execute(sql,val)
                common_name_list = cur.fetchall()
                
                return render_template(
                    "search_fish_common_name_page.html",
                    common_name_list = common_name_list,
                    common_name_doc = common_name_doc
                )
    else:
        return redirect(url_for("AdminLogin"))

@app.route("/search_fish_name" , methods=["GET" , "POST"])
def search_fish_name():
    if session.get("admin",None) is not None:
        if request.method=="POST":
            Fish_name = request.form['search_name']
            common_name_doc = common_name_document()
            with sqlite3.connect("..\mydata.db") as connect:
                cur = connect.cursor()

                sql = "SELECT * FROM fish_data WHERE name LIKE ?"
                val = ['%'+Fish_name+'%']
                cur.execute(sql,val)
                common_name_list = cur.fetchall()
                
                return render_template(
                    "search_fish_name_page.html",
                    common_name_list = common_name_list,
                    common_name_doc = common_name_doc
                )
    else:
        return redirect(url_for("AdminLogin"))

@app.route("/delete_fish", methods=["GET", "POST"])
def delete_fish():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            no = request.form.get("no")
            print(no)
            with sqlite3.connect("..\mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("DELETE FROM fish_data where No= ? ",[no])
                connect.commit()
            return redirect(url_for('goto_fishpage'))

@app.route("/delete_common_name", methods=["GET", "POST"])
def delete_common_name():
    if session.get("admin",None) is not None:
        if request.method == "POST":
            id = request.form.get("id")
            with sqlite3.connect("..\mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("DELETE FROM common_name where id= ? ",[id])
                connect.commit()
            return redirect(url_for('goto_fishpage'))

################################################
@app.route('/')
def gotoAdminpage():
    if session.get("admin",None) is not None:
        admin = str(session.get("admin"))
        return redirect(url_for("goto_shoppage"))
    else:
        return redirect(url_for("AdminLogin"))

@app.route('/login',methods=["POST", "GET"])
def AdminLogin():
    if request.method == "POST":
        session.pop('admin',None)
        username = request.form.get("username")
        password = request.form.get("password")
        print(username)
        print(password)
        get_user = '$5$rounds=535000$b9PDkfXZO5DXmRJF$JWgW4N7lw554ay3ujlsEau1aF3Y5PSB4mb5DyaeuCyB'
        get_password = '$5$rounds=535000$/Jd1udZna8KVXJR2$rucB85v9/I4jO/AR/ZbCzvvVUar/nuxfbUy1.x2aw.5'
        if(sha256_crypt.verify(password, get_password)):
            if(sha256_crypt.verify(username, get_user)):
                session['admin'] = request.form['username']
                print(session)
                return redirect(url_for("gotoAdminpage"))
            else:
                flash("รหัสผ่านหรืออีเมลไม่ถูกต้อง","danger")
        else:
            flash("รหัสผ่านหรืออีเมลไม่ถูกต้อง","danger")
    else:
        return render_template("login_admin.html")

@app.route("/admin_pages")
def getadmin():
    if session.get("admin",None) is not None:
        admin = str(session.get("admin"))
        return render_template("header_admin.html")
    else:
        return redirect(url_for("AdminLogin"))

@app.route("/fish_pages")
def goto_fishpage():
    if session.get("admin",None) is not None:
        admin = str(session.get("admin"))
        fish_data = fish_document()
        common_name_doc = common_name_document()
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            page, per_page, offset = get_page_args(
                page_parameter='page', 
                per_page_parameter='per_page'
            )
            sql = "SELECT * FROM fish_data ORDER BY No LIMIT ? OFFSET ?"
            val = [per_page, offset]
            cur.execute(sql,val)
            fish_data_list = cur.fetchall()
            fish_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=len(fish_data),
                css_framework='bootstrap4'
            )
            return render_template(
                "fish_page.html",
                fish_data_list = fish_data_list,
                fish_pagination = fish_pagination,
                common_name_doc =common_name_doc
            )
    else:
        return redirect(url_for("AdminLogin"))

@app.route("/shop_pages")
def goto_shoppage():
    if session.get("admin",None) is not None:
        admin = str(session.get("admin"))
        shop_doc = shop_document()
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            page, per_page, offset = get_page_args(
                page_parameter='page', 
                per_page_parameter='per_page'
            )
            sql = "SELECT * FROM seller ORDER BY seller_ID LIMIT ? OFFSET ?"
            val = [per_page, offset]
            cur.execute(sql,val)
            shop_data_list = cur.fetchall()
            shop_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=len(shop_doc),
                css_framework='bootstrap4'
            )
            return render_template(
                "shop_page.html",
                shop_data_list = shop_data_list,
                shop_pagination = shop_pagination
            )
    else:
        return redirect(url_for("AdminLogin"))

@app.route("/common_name_pages")
def goto_common_name():
    if session.get("admin",None) is not None:
        admin = str(session.get("admin"))
        common_name_doc = common_name_document()
        with sqlite3.connect("..\mydata.db") as connect:
            cur = connect.cursor()
            page, per_page, offset = get_page_args(
                page_parameter='page', 
                per_page_parameter='per_page'
            )
            sql = "SELECT * FROM common_name ORDER BY id LIMIT ? OFFSET ?"
            val = [per_page, offset]
            cur.execute(sql,val)
            common_name_list = cur.fetchall()
            common_name_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=len(common_name_doc),
                css_framework='bootstrap4'
            )
            
            return render_template(
                "fish_common_name_page.html",
                common_name_list = common_name_list,
                common_name_pagination = common_name_pagination,
                common_name_doc = common_name_doc
            )
    else:
        return redirect(url_for("AdminLogin"))

if __name__ == "__main__":
    app.secret_key = "fhu1234567803102541fhu"
    app.run(host="localhost", port=5000, debug=True)
