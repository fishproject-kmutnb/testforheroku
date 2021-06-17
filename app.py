from flask import Flask ,flash, render_template ,request, jsonify,redirect,url_for , session ,g
from flask_paginate import Pagination, get_page_args , get_page_parameter
from flask_mail import Mail , Message


#from keras.models import load_model


#from keras.preprocessing.image import load_img, img_to_array
#from keras_preprocessing import image

from passlib.hash import sha256_crypt
#import cv2
import smtplib
import numpy as np
import os
import uuid
import sqlite3

import datetime
from datetime import date

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = "/static/images"

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'fishservice63@gmail.com'
app.config['MAIL_PASSWORD'] = '@Abcde11'
app.config['MAIL_DEFAULT_SENDER'] = 'fishservice63@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
# app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)
######################## MAILER ########################
@app.route("/sendmail",methods=['GET','POST'])
def sendmail():

    x = datetime.datetime.now()
    Date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
    Time = x.strftime("%X")

    if session.get("user",None) is not None:
        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                username = session['user']
                if basketValidate(username):
                    total = request.form['total']
                    status = request.form['status']
                    sendmailseller(total,status)
                    cur = connect.cursor()

                    sql = "update history SET status = ? WHERE username  = ?"
                    val = [
                        status,
                        username
                    ]      
                    cur.execute(sql,(val))

                    cur.execute("select * from basket where username = ? and status = ?",[username,"in-cart"])
                    basket = cur.fetchall()[0]
                    basket_data = list(basket)
                    basket_data = tuple(basket_data)

                    sql = "update basket SET status = ? WHERE username  = ?"
                    val = [
                        status,
                        username
                    ]                        
                    print(val)
                    cur.execute(sql,(val))

                    cur.execute("select * from user where user_ID = ?",[username])
                    user = cur.fetchall()[0]
                    user_data = list(user)
                    user_data = tuple(user_data)
                    print (user_data[0])
                    email = request.form.get("")
                    msg = Message('OrnamentalFish Platform',recipients=[user_data[3]])
                    body = (''' 
                        <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                table, th, td {
                                    border: 1px solid black;
                                    border-collapse: collapse;
                                }
                                th, td {
                                    padding: 5px;
                                    text-align: left;
                                }
                                </style>
                            </head>
                            <body>
                            <div class="container my-0 bg">   
                                <div class="card-body row gy-2 gx-2">
                                    <div class="col-xs-12 col-md-12">
                                        <h2 align="center">คุณได้สั่งซื้อสินค้าจาก Ornamentalfish Platform ที่ร้าน '''+basket_data[7]+'''</h2>
                                        <h4 align="center">สั่งซื้อวันที่ : '''+Date+" "+Time+'''</h4>
                                        <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                        <h4>ที่อยู่ : '''+user_data[5]+'''</h4>
                                        <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                        <h4>Email : '''+user_data[3]+'''</h4>
                                        
                                        <h4>กรุณาติดต่อช่องทางการโอนเงินไปยังร้านค้าแล้วแนปสลิปไปที่รายการสั่งซื้อของคุณทางหน้าข้อมูลส่วนตัว</h4>
                                    </div>
                                </div>
                            </div>
                            </body>
                            </html>            
                        ''')
                    msg.html = body
                    mail.send(msg)
                    return render_template('buysuccess_user.html',user = session['user'])
                else:
                    flash("คุณยังไม่มีสินค้าในตะกร้า","danger")
                    return redirect(url_for('basket'))
                    
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                username = session['user']
                if basketValidate(username):
                    total = request.form['total']
                    status = request.form['status']
                    sendmailseller(total,status)
                    cur = connect.cursor()

                    sql = "update history SET status = ? WHERE username  = ? and status = ?"
                    val = [
                        status,
                        username,
                        'in-cart'
                    ]      
                    cur.execute(sql,(val))

                    cur.execute("select * from basket where username = ? and status = ?",[username,"in-cart"])
                    basket = cur.fetchall()[0]
                    basket_data = list(basket)
                    basket_data = tuple(basket_data)

                    sql = "update basket SET status = ? WHERE username  = ? and status = ?"
                    val = [
                        status,
                        username,
                        'in-cart'
                    ]                        
                    print(val)
                    cur.execute(sql,(val))

                    cur.execute("select * from seller where seller_ID = ?",[username])
                    user = cur.fetchall()[0]
                    user_data = list(user)
                    user_data = tuple(user_data)
                    email = request.form.get("")
                    msg = Message('OrnamentalFish Platform',recipients=[user_data[3]])
                    body = (''' 
                        <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                table, th, td {
                                    border: 1px solid black;
                                    border-collapse: collapse;
                                }
                                th, td {
                                    padding: 5px;
                                    text-align: left;
                                }
                                </style>
                            </head>
                            <body>
                            <div class="container my-0 bg">   
                                <div class="card-body row gy-2 gx-2">
                                    <div class="col-xs-12 col-md-12">
                                        <h2 align="center">คุณได้สั่งซื้อสินค้าจาก Ornamentalfish Platform ที่ร้าน '''+basket_data[7]+'''</h2>
                                        <h4 align="center">สั่งซื้อวันที่ : '''+Date+" "+Time+'''</h4>
                                        <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                        <h4>ที่อยู่ : '''+user_data[5]+''''</h4>
                                        <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                        <h4>Email : '''+user_data[3]+'''</h4>
                                        
                                        <h4>กรุณาติดต่อช่องทางการโอนเงินไปยังร้านค้าแล้วแนปสลิปไปที่รายการสั่งซื้อของคุณทางหน้าข้อมูลส่วนตัว</h4>
                                    </div>
                                </div>
                            </div>
                            </body>
                            </html>            
                        ''')
                    msg.html = body
                    mail.send(msg)
                    return render_template('buysuccess_seller.html',seller = session['user'])
                else:
                    flash("คุณยังไม่มีสินค้าในตะกร้า","danger")
                    return redirect(url_for('basket'))

@app.route("/sendmailseller")
def sendmailseller(total,status):
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                username = session['user']
                x = datetime.datetime.now()
                Date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
                Time = x.strftime("%X")
                cur = connect.cursor()
                cur.execute("select * from basket where username = ? and status = ?",[username,"in-cart"])
                basket = cur.fetchall()[0]
                basket_data = list(basket)
                basket_data = tuple(basket_data)

                cur.execute("select * from seller where seller_ID = ?",[username])
                user = cur.fetchall()[0]
                user_data = list(user)
                user_data = tuple(user_data)
                print (user_data[0])

                cur.execute("select * from seller where seller_Storename = ?",[basket_data[7]])
                seller = cur.fetchall()[0]
                seller_data = list(seller)
                seller_data = tuple(seller_data)
                email = request.form.get("")
                msg = Message('OrnamentalFish Platform',recipients=[seller_data[3]])
                body = (''' 
                    <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                table, th, td {
                                    border: 1px solid black;
                                    border-collapse: collapse;
                                }
                                th, td {
                                    padding: 5px;
                                    text-align: left;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container my-0 bg">   
                                <div class="card-body row gy-2 gx-2">
                                    <div class="col-xs-12 col-md-12">
                                        <h2 align="center">มีผู้ใช้ได้สั่งซื้อสินค้าจากร้านของคุณที่ Ornamentalfish Platform </h2>
                                        <h4 align="center">สั่งซื้อวันที่ : '''+Date+" "+Time+'''</h4>
                                        <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                        <h4>ที่อยู่ : '''+user_data[5]+''''</h4>
                                        <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                        <h4>Email : '''+user_data[3]+'''</h4>
                                        
                                        <h4>กรุณาติดต่อช่องทางการโอนเงินไปยังผู้ใช้และรอการชำระเงิน สามารถตรวจสอบสลิปหรือเปลี่ยนสถานะการสั่งซื้อได้ที่หน้าข้อมูลส่วนตัว</h4>
                                    </div>
                                </div>
                            </div>
                        </body>
                        </html>            
                        ''')
                msg.html = body
                mail.send(msg)

        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                username = session['user']
                x = datetime.datetime.now()
                Date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
                Time = x.strftime("%X")
                cur = connect.cursor()
                status = request.form['status']
                cur = connect.cursor()

                cur.execute("select * from basket where username = ? and status = ?",[username,"in-cart"])
                basket = cur.fetchall()[0]
                basket_data = list(basket)
                basket_data = tuple(basket_data)

                cur.execute("select * from user where user_ID = ?",[username])
                user = cur.fetchall()[0]
                user_data = list(user)
                user_data = tuple(user_data)
                print (user_data[0])

                cur.execute("select * from seller where seller_Storename = ?",[basket_data[7]])
                seller = cur.fetchall()[0]
                seller_data = list(seller)
                seller_data = tuple(seller_data)

                email = request.form.get("")
                msg = Message('OrnamentalFish Platform',recipients=[seller_data[3]])
                body = (''' 
                    <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                table, th, td {
                                    border: 1px solid black;
                                    border-collapse: collapse;
                                }
                                th, td {
                                    padding: 5px;
                                    text-align: left;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container my-0 bg">   
                                <div class="card-body row gy-2 gx-2">
                                    <div class="col-xs-12 col-md-12">
                                        <h2 align="center">มีผู้ใช้ได้สั่งซื้อสินค้าจากร้านของคุณที่ Ornamentalfish Platform </h2>
                                        <h4 align="center">สั่งซื้อวันที่ : '''+Date+" "+Time+'''</h4>
                                        <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                        <h4>ที่อยู่ : '''+user_data[5]+''''</h4>
                                        <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                        <h4>Email : '''+user_data[3]+'''</h4>
                                        
                                        <h4>กรุณาติดต่อช่องทางการโอนเงินไปยังผู้ใช้และรอการชำระเงิน สามารถตรวจสอบสลิปหรือเปลี่ยนสถานะการสั่งซื้อได้ที่หน้าข้อมูลส่วนตัว</h4>
                                    </div>
                                </div>
                            </div>
                        </body>
                        </html>            
                        ''')
                msg.html = body
                mail.send(msg)

@app.route("/sendmailslip")
def sendmailslip(history_id,filepath):
    if session.get("role") == 'seller':
        with sqlite3.connect("mydata.db") as connect:
            username = session['user']
            x = datetime.datetime.now()
            Date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
            Time = x.strftime("%X")
            cur = connect.cursor()
            #history_id = request.form.get["history_id"]

            cur.execute("select * from seller where seller_ID = ?",[username])
            user = cur.fetchall()[0]
            user_data = list(user)
            user_data = tuple(user_data)

            cur.execute("select * from history where username = ? and id = ?",[username,history_id])
            history = cur.fetchall()[0]
            history_data = list(history)
            history_data = tuple(history_data)

            cur.execute("select * from seller where seller_Storename = ?",[history_data[7]])
            seller = cur.fetchall()[0]
            seller_data = list(seller)
            seller_data = tuple(seller_data) 

            email = request.form.get("")
            msg = Message('OrnamentalFish Platform',recipients=[seller_data[3]])
            body = (''' 
                <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                            }
                            th, td {
                                padding: 5px;
                                text-align: left;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container my-0 bg">   
                            <div class="card-body row gy-2 gx-2">
                                <div class="col-xs-12 col-md-12">
                                    <h2 align="center">คุณ'''+user_data[0]+'''ได้ส่งสลิปโอนเงินการสั่งซื้อสินค้าจากร้านของคุณที่ Ornamentalfish Platform </h2>
                                    <h4 align="center">เมื่อวันวันที่ : '''+Date+" "+Time+'''</h4>
                                    <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                    <h4>ที่อยู่ : '''+user_data[5]+'''</h4>
                                    <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                    <h4>Email : '''+user_data[3]+'''</h4>
                                    <h4>กรุณาตรวจสอบหลักฐานการโอนเงิน และเปลี่ยนสถานะการสั่งซื้อที่หน้าข้อมูลส่วนตัว</h4>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>            
                ''')
            msg.html = body
            with app.open_resource(""+filepath+"") as slip:
                msg.attach(""+filepath+"","images/jpeg", slip.read())
            mail.send(msg)

    if session.get("role") == 'user':
        with sqlite3.connect("mydata.db") as connect:
            username = session['user']
            x = datetime.datetime.now()
            Date =x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
            Time = x.strftime("%X")
            cur = connect.cursor()
            #history_id = request.form.get["history_id"]

            cur.execute("select * from user where user_ID = ?",[username])
            user = cur.fetchall()[0]
            user_data = list(user)
            user_data = tuple(user_data)

            cur.execute("select * from history where username = ? and id = ?",[username,history_id])
            history = cur.fetchall()[0]
            history_data = list(history)
            history_data = tuple(history_data)

            cur.execute("select * from seller where seller_Storename = ?",[history_data[7]])
            seller = cur.fetchall()[0]
            seller_data = list(seller)
            seller_data = tuple(seller_data) 

            email = request.form.get("")
            msg = Message('OrnamentalFish Platform',recipients=[seller_data[3]])
            body = (''' 
                <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                            }
                            th, td {
                                padding: 5px;
                                text-align: left;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container my-0 bg">   
                            <div class="card-body row gy-2 gx-2">
                                <div class="col-xs-12 col-md-12">
                                    <h2 align="center">คุณ'''+user_data[0]+'''ได้ส่งสลิปโอนเงินการสั่งซื้อสินค้าจากร้านของคุณที่ Ornamentalfish Platform </h2>
                                    <h4 align="center">เมื่อวันวันที่ : '''+Date+" "+Time+'''</h4>
                                    <h4>ชื่อ : '''+user_data[1]+" "+user_data[2]+'''</h4>
                                    <h4>ที่อยู่ : '''+user_data[5]+'''</h4>
                                    <h4>เบอร์โทรศัพท์ : '''+user_data[4]+'''</h4>
                                    <h4>Email : '''+user_data[3]+'''</h4>
                                    <h4>กรุณาตรวจสอบหลักฐานการโอนเงิน และเปลี่ยนสถานะการสั่งซื้อที่หน้าข้อมูลส่วนตัว</h4>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>            
                ''')
            msg.html = body
            with app.open_resource(""+filepath+"") as slip:
                msg.attach(""+filepath+"","images/jpeg", slip.read())
            mail.send(msg)


@app.route("/sendmailconfirm",methods=['GET','POST'])
def sendmailconfirm(buyer,id):
    if session.get("role") == 'seller':
        with sqlite3.connect("mydata.db") as connect:
            username = session['user']
            x = datetime.datetime.now()
            Date = x.strftime("%Y") + '-' + x.strftime("%m") + '-' + x.strftime("%d")
            Time = x.strftime("%X")
            cur = connect.cursor()
            print(buyer)
            cur.execute("select user_email from user where user_ID = ? UNION select seller_email from seller where seller_ID = ?",[buyer,buyer])
            user = cur.fetchall()[0]
            print(user)
            user_data = list(user)
            user_data = tuple(user_data)    

            #if not user :
            #    print(buyer)
            #    cur.execute("select * from user where user_id = ?",[buyer])
            #    user = cur.fetchall()[0]
            #    user_data = list(user)
            #    user_data = tuple(user_data)
            
            cur.execute("select * from history where id = ?",[id])
            history = cur.fetchall()[0]
            history_data = list(history)
            history_data = tuple(history_data)

            email = request.form.get("")
            msg = Message('OrnamentalFish Platform',recipients=[user_data[0]])
            body = (''' 
                <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                        table, th, td {
                                border: 1px solid black;
                                border-collapse: collapse;
                        }
                        th, td {
                            padding: 5px;
                            text-align: left;
                        }
                        </style>
                    </head>
                    <body>
                    <div class="container my-0 bg">   
                        <div class="card-body row gy-2 gx-2">
                            <div class="col-xs-12 col-md-12">
                                <h2 align="center">คำสั่งซื้อของคุณจาก Ornamentalfish Platform ที่ร้าน '''+history_data[7]+''' ได้รับการอนุมัติแล้ว</h2>
                                <h3 align="center">สินค้า : '''+str(history_data[2])+'''</h3>
                                <h3 align="center">จำนวน : '''+str(history_data[5])+'''</h3>
                                <h3 align="center">ราคา : '''+str(history_data[3])+'''</h3>                            
                            </div>
                        </div>
                    </div>
                    </body>
                    </html>            
                ''')
            msg.html = body
            mail.send(msg)


################UPLOAD-FOR-CLASSIFICATION###############
@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        if request.files:
            file = request.files["image"]
            filepath = "./static/images/image.jpg"
            file.save(filepath)
    return redirect(url_for('showData'))

@app.route("/predict")
def getPrediction():
    # img = load_img("./static/images/image.jpg", target_size = (300, 300))
    img = cv2.imread(os.path.join("./static/images", "image.jpg"))
    img = cv2.resize(img, (300,300))
    img = image.img_to_array(img)
    img = img.reshape(1, 300, 300, 3)
    img = np.array(img)/255
    model = load_model("modelv2.h5")
    # img = img_to_array(img)
    # img = img.reshape(1, 300, 300, 3)
    # img = img.astype('uint8')
    result = model.predict(img)[0]
    # accuracy = result[np.argmax(result)]
    # print(accuracy)
    return result
######################## VALIDATION ####################
@app.route("/basketValidate")
def basketValidate(username):
    print(username)
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT * FROM basket WHERE username = ? AND status = ?"
        val = [username,"in-cart"]
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

@app.route("/StockValidateFish")
def StockValidateFish(fish_id,count):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT fish_Amount FROM fish_product WHERE fish_ID = ?"
        val = [fish_id,]
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(count) == 0:
            return False
        else:
            count = int(count)
            if result[0][0] < count:
                return False
            else:
                sql = "UPDATE fish_product SET fish_amount = ? WHERE fish_ID = ?"
                val = [result[0][0]-count,fish_id]
                cur.execute(sql , val)
                return True

@app.route("/StockValidateTool")
def StockValidateTool(tool_id,count):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT tool_Amount FROM tool_product WHERE tool_ID = ?"
        val = [tool_id,]
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(count) == 0:
            return False
        else:
            count = int(count)
            if result[0][0] < count:
                return False
            else:
                sql = "UPDATE tool_product SET tool_amount = ? WHERE tool_ID = ?"
                val = [result[0][0]-count,tool_id]
                cur.execute(sql , val)
                return True

@app.route("/StockValidateAccessories")
def StockValidateAccessories(accessories_id,count):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT accessories_Amount FROM accessories_product WHERE accessories_ID = ?"
        val = [accessories_id]
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(count) == 0:
            return False
        else:
            count = int(count)
            if result[0][0] < count:
                return False
            else:
                sql = "UPDATE accessories_product SET accessories_amount = ? WHERE accessories_ID = ?"
                val = [result[0][0]-count,accessories_id]
                cur.execute(sql , val)
                return True

@app.route("/selleridValidate")
def selleridValidate(username):
    print(username)
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT seller_ID FROM seller WHERE seller_ID = ?"
        val = [username]
        # cur.execute("SELECT seller_ID FROM seller WHERE seller_ID = ?" , [username])
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(result) == 0:
            return True
        else:
            return False

@app.route("/useridValidate")
def useridValidate(username):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT user_ID FROM user WHERE user_ID = ?"
        val = [username]
        cur.execute(sql , val)
        result = cur.fetchall()
        if len(result) == 0:
            return True
        else:
            return False

@app.route("/selleremailValidate")
def selleremailValidate(email):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT seller_Email FROM seller WHERE seller_Email = ?"
        val = [email]
        cur.execute(sql , val)
        result = cur.fetchall()
        lenresult = len(result)
        if len(result) == 0:
            return True
        else:
            return False

@app.route("/useremailValidate")
def useremailValidate(email):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT user_Email FROM user WHERE user_Email = ?"
        val = [email]
        cur.execute(sql , val)
        result = cur.fetchall()
        lenresult = len(result)
        if len(result) == 0:
            return True
        else:
            return False

@app.route("/sellerStoreValidate")
def sellerStoreValidate(storename):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "SELECT seller_Storename FROM seller WHERE seller_Storename = ?"
        val = [storename]
        cur.execute(sql , val)
        result = cur.fetchall()
        lenresult = len(result)
        if len(result) == 0:
            return True
        else:
            return False
###########################FEATURE##########################
@app.route("/alert_login")
def alert_login():
    return render_template("alert_login.html")

@app.route("/dropsession")
def dropsession():
    session.pop('user',None)
    session.clear()
    return redirect(url_for('home'))

@app.route("/edit_fish" , methods=["GET","POST"])
def edit_fish():
    if session.get("user",None) is not None:
        if request.method=="POST":
            fish_name = str(request.form.get("edit_name"))
            fish_price = request.form.get("edit_price")
            fish_amount = request.form.get("edit_amount")
            fish_description = request.form.get("edit_description")
            fish_id = request.form.get("edit_id")
            print(fish_id)
            if fish_amount.isnumeric():
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    sql = "UPDATE fish_product SET fish_Name = ?,fish_Price = ?,fish_Amount = ?,fish_description = ? WHERE fish_ID  = ?"
                    val = [
                        fish_name,
                        fish_price,
                        fish_amount,
                        fish_description,
                        fish_id
                    ]                        
                    print(val)
                    cur.execute(sql,val)
                    connect.commit()
                return redirect(url_for('ownerproduct_fish'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","warning")
                return redirect(url_for('ownerproduct_fish'))
    else:
        return redirect(url_for('home'))

@app.route("/edit_accessories" , methods=["GET","POST"])
def edit_accessories():
    if session.get("user",None) is not None:
        if request.method=="POST":
            accessories_name = str(request.form.get("edit_name"))
            accessories_price = request.form.get("edit_price")
            accessories_amount = request.form.get("edit_amount")
            accessories_description = request.form.get("edit_description")
            accessories_id = request.form.get("edit_id")

            if accessories_amount.isnumeric():
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    sql = "UPDATE accessories_product SET accessories_Name = ?,accessories_Price = ?,accessories_Amount = ?,accessories_description = ? WHERE accessories_ID  = ?"
                    val = [
                        accessories_name,
                        accessories_price,
                        accessories_amount,
                        accessories_description,
                        accessories_id
                    ]                        
                    print(val)
                    cur.execute(sql,val)
                    connect.commit()
                return redirect(url_for('ownerproduct_accessories'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","warning")
                return redirect(url_for('ownerproduct_accessories'))
    else:
        return redirect(url_for('home'))

@app.route("/edit_tool" , methods=["GET","POST"])
def edit_tool():
    if session.get("user",None) is not None:
        if request.method=="POST":
            tool_name = str(request.form.get("edit_name"))
            tool_price = request.form.get("edit_price")
            tool_amount = request.form.get("edit_amount")
            tool_description = request.form.get("edit_description")
            tool_id = request.form.get("edit_id")

            if tool_amount.isnumeric():
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    sql = "UPDATE tool_product SET tool_Name = ?,tool_Price = ?,tool_Amount = ?,tool_description = ? WHERE tool_ID  = ?"
                    val = [
                        tool_name,
                        tool_price,
                        tool_amount,
                        tool_description,
                        tool_id
                    ]                        
                    print(val)
                    cur.execute(sql,val)
                    connect.commit()
                return redirect(url_for('ownerproduct_tool'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","warning")
                return redirect(url_for('ownerproduct_tool'))
    else:
        return redirect(url_for('home'))

@app.route("/add_fish", methods=["GET", "POST"])
def add_fish():
    if session.get("user",None) is not None:
        if request.method=="POST":
            fish_Owner = str(session.get("user"))
            fish_name = str(request.form.get("fish_name"))
            fish_price = request.form.get("fish_price")
            fish_amount = request.form.get("fish_amount")
            fish_description = request.form.get("fish_description")
            x = datetime.datetime.now()            
            if fish_amount.isnumeric():
                if request.files:
                    path_pic = "static\\images\\product_fish_images\\"+str(uuid.uuid4())+".jpg"
                    print(fish_Owner+" "+fish_name+" "+fish_price+" "+fish_amount+" "+fish_description+" "+path_pic)
                    file = request.files["fish_pic"]
                    filepath = path_pic
                    file.save(filepath)
                    with sqlite3.connect("mydata.db") as connect:
                        cur = connect.cursor()
                        sql = "INSERT INTO fish_product(fish_Name,fish_Owner,fish_Price,fish_Amount,fish_description,fish_Images,fish_select_count,time) VALUES(?,?,?,?,?,?,?,?)"
                        val = [
                            fish_name,
                            fish_Owner,
                            float(fish_price),
                            int(fish_amount),
                            fish_description,
                            path_pic,
                            0,
                            x
                        ]
                        cur.execute(sql,val)
                        connect.commit()
                return redirect(url_for('ownerproduct_fish'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","warning")
                return redirect(url_for('ownerproduct_fish'))
    else:
        return redirect(url_for('home'))

@app.route("/add_basket_fish",methods=["POST","GET"])
def add_basket_fish():
    x = datetime.datetime.now()
    date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                user = session['user']
                Fish_ID = request.form['fish_id']
                Count = request.form['count']
                if StockValidateFish(Fish_ID,Count):   
                    cur = connect.cursor()
                    sql = ("UPDATE fish_product SET fish_select_count = fish_select_count + 1 WHERE fish_ID = ?")
                    val = [Fish_ID]
                    cur.execute(sql , val)
                    # cur.execute("SELECT * FROM fish_product WHERE fish_id = ?",[Fish_ID])
                    cur.execute("SELECT fish_product.* , seller.seller_Storename FROM fish_product INNER JOIN seller ON seller.seller_ID=fish_product.fish_Owner WHERE  fish_ID = ?",[Fish_ID])
                    Fish_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Fish_product_data[1],Fish_product_data[3],Count,Fish_product_data[6],Fish_product_data[9],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Fish_product_data[1],Fish_product_data[3],Count,Fish_product_data[6],Fish_product_data[9],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return redirect(url_for('fish_product'))
    else:
        return redirect(url_for('alert_login'))

@app.route("/add_basket_fish_shop",methods=["POST","GET"])
def add_basket_fish_shop():
    x = datetime.datetime.now()
    date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                shop_id = request.form['seller_id']
                user = session['user']
                Fish_ID = request.form['fish_id']
                Count = request.form['count']
                if StockValidateFish(Fish_ID,Count):   
                    cur = connect.cursor()
                    sql = ("UPDATE fish_product SET fish_select_count = fish_select_count + 1 WHERE fish_ID = ?")
                    val = [Fish_ID]
                    cur.execute(sql , val)
                    # cur.execute("SELECT * FROM fish_product WHERE fish_id = ?",[Fish_ID])
                    cur.execute("SELECT fish_product.* , seller.seller_Storename FROM fish_product INNER JOIN seller ON seller.seller_ID=fish_product.fish_Owner WHERE  fish_ID = ?",[Fish_ID])
                    Fish_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Fish_product_data[1],Fish_product_data[3],Count,Fish_product_data[6],Fish_product_data[9],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Fish_product_data[1],Fish_product_data[3],Count,Fish_product_data[6],Fish_product_data[9],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return shop_fish(shop_id)
    else:
        return redirect(url_for('alert_login'))

@app.route("/add_basket_accessories",methods=["POST","GET"])
def add_basket_accessories():
    x = datetime.datetime.now()
    date = x.strftime("%d")+ '/' +x.strftime("%m")   + '/' +  x.strftime("%Y")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                user = session['user']
                Accessories_ID = request.form['accessories_id']
                Count = request.form['count']
                if StockValidateAccessories(Accessories_ID,Count):
                    cur = connect.cursor()
                    cur.execute("SELECT accessories_product.* , seller.seller_Storename FROM accessories_product INNER JOIN seller ON seller.seller_ID=accessories_product.accessories_Owner WHERE accessories_id = ?",[Accessories_ID])
                    Accessories_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Accessories_product_data[1],Accessories_product_data[2],Count,Accessories_product_data[5],Accessories_product_data[8],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Accessories_product_data[1],Accessories_product_data[2],Count,Accessories_product_data[5],Accessories_product_data[8],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return redirect(url_for('accessories_product'))
    else:
        return redirect(url_for('alert_login'))

@app.route("/add_basket_accessories_shop",methods=["POST","GET"])
def add_basket_accessories_shop():
    x = datetime.datetime.now()
    date = x.strftime("%Y") + '-' + x.strftime("%m") + '-' + x.strftime("%d")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                shop_id = request.form['seller_id']
                user = session['user']
                Accessories_ID = request.form['accessories_id']
                Count = request.form['count']
                if StockValidateAccessories(Accessories_ID,Count):
                    cur = connect.cursor()
                    cur.execute("SELECT accessories_product.* , seller.seller_Storename FROM accessories_product INNER JOIN seller ON seller.seller_ID=accessories_product.accessories_Owner WHERE accessories_id = ?",[Accessories_ID])
                    Accessories_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Accessories_product_data[1],Accessories_product_data[2],Count,Accessories_product_data[5],Accessories_product_data[8],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Accessories_product_data[1],Accessories_product_data[2],Count,Accessories_product_data[5],Accessories_product_data[8],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return shop_accessories(shop_id)
    else:
        return redirect(url_for('alert_login'))

@app.route("/add_basket_tool",methods=["POST","GET"])
def add_basket_tool():
    x = datetime.datetime.now()
    date = x.strftime("%Y") + '-' + x.strftime("%m") + '-' + x.strftime("%d")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                user = session['user']
                Tool_ID = request.form['tool_id']
                Count = request.form['count']
                if StockValidateTool(Tool_ID,Count):
                    cur = connect.cursor()
                    cur.execute("SELECT tool_product.* , seller.seller_Storename FROM tool_product INNER JOIN seller ON seller.seller_ID=tool_product.tool_Owner WHERE tool_id = ?",[Tool_ID])
                    Tool_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Tool_product_data[1],Tool_product_data[2],Count,Tool_product_data[5],Tool_product_data[8],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Tool_product_data[1],Tool_product_data[2],Count,Tool_product_data[5],Tool_product_data[8],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return redirect(url_for('tool_product'))
    else:
        return redirect(url_for('alert_login'))

@app.route("/add_basket_tool_shop",methods=["POST","GET"])
def add_basket_tool_shop():
    x = datetime.datetime.now()
    date = x.strftime("%Y") + '-' + x.strftime("%m") + '-' + x.strftime("%d")
    time = x.strftime("%X")
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                shop_id = request.form['seller_id']
                user = session['user']
                Tool_ID = request.form['tool_id']
                Count = request.form['count']
                if StockValidateTool(Tool_ID,Count):
                    cur = connect.cursor()
                    cur.execute("SELECT tool_product.* , seller.seller_Storename FROM tool_product INNER JOIN seller ON seller.seller_ID=tool_product.tool_Owner WHERE tool_id = ?",[Tool_ID])
                    Tool_product_data = cur.fetchall()[0]
                    sql = "INSERT INTO basket(username,product_Name,price,count,image,shop,date,time,status) VALUES(?,?,?,?,?,?,?,?,?)"
                    val = [user,Tool_product_data[1],Tool_product_data[2],Count,Tool_product_data[5],Tool_product_data[8],date,time,'in-cart']
                    cur.execute(sql , val)
                    sql = "INSERT INTO history(username,product_Name,price,count,image,shop,date,time,status,status_product,slip_image) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
                    val = [user,Tool_product_data[1],Tool_product_data[2],Count,Tool_product_data[5],Tool_product_data[8],date,time,'in-cart','in-cart','none']
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('basket'))
                else:
                    flash("จำนวนสินค้าไม่เพียงพอ","danger")
                    return shop_tool(shop_id)
    else:
        return redirect(url_for('alert_login'))

@app.route("/delete_basket",methods=["POST","GET"])
def delete_basket():
    if session.get("user",None) is not None:
        if request.method=="POST":
            with sqlite3.connect("mydata.db") as connect:
                user = session['user']
                id = request.form['id']
                cur = connect.cursor()

                sql = "DELETE FROM basket WHERE id = ? AND  username = ?"
                val=[id,user]
                cur.execute(sql,val)

                sql = "DELETE FROM history WHERE id = ? AND  username = ?"
                val=[id,user]
                cur.execute(sql,val)

                connect.commit()
        return redirect(url_for('basket'))

@app.route("/delete_fish", methods=["GET", "POST"])
def delete_fish():
    if session.get("user",None) is not None:
        if request.method=="POST":
            fish_id = request.form.get("fish_id")
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "DELETE FROM fish_product WHERE fish_ID = ?"
                val=[fish_id]
                cur.execute(sql,val)
                connect.commit()
                return redirect(url_for('ownerproduct_fish'))
    else:
        return redirect(url_for('home'))

@app.route("/delete_accessories", methods=["GET", "POST"])
def delete_accessories():
    if session.get("user",None) is not None:
        if request.method=="POST":
            accessories_id = request.form.get("accessories_id")
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "DELETE FROM accessories_product WHERE accessories_ID = ?"
                val = [accessories_id]
                cur.execute(sql,val)
                connect.commit()
                return redirect(url_for('ownerproduct_accessories'))
    else:
        return redirect(url_for('home'))        

@app.route("/delete_tool", methods=["GET", "POST"])
def delete_tool():
    if session.get("user",None) is not None:
        if request.method=="POST":
            tool_id = request.form.get("tool_id")
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "DELETE FROM tool_product WHERE tool_ID = ?"
                val=[tool_id]
                cur.execute(sql,val)
                connect.commit()
                return redirect(url_for('ownerproduct_tool'))
    else:
        return redirect(url_for('home'))  

@app.route("/add_tool", methods=["GET", "POST"])
def add_tool():
    if session.get("user",None) is not None:
        if request.method=="POST":
            tool_Owner = str(session.get("user"))
            tool_name = str(request.form.get("tool_name"))
            tool_price = request.form.get("tool_price")
            tool_amount = request.form.get("tool_amount")
            tool_description = request.form.get("tool_description")
            x = datetime.datetime.now() 
            if tool_price.isnumeric() and tool_amount.isnumeric():
                if request.files:
                    path_pic = "static\\images\\product_tool_images\\"+str(uuid.uuid4())+".jpg"
                    file = request.files["tool_pic"]
                    filepath = path_pic
                    file.save(filepath)
                    with sqlite3.connect("mydata.db") as connect:
                        cur = connect.cursor()
                        sql = "INSERT INTO tool_product(tool_Owner,tool_Name,tool_Price,tool_Amount,tool_description,tool_Images,time) VALUES(?,?,?,?,?,?,?)"
                        val = [
                            tool_Owner,
                            tool_name,
                            float(tool_price),
                            int(tool_amount),
                            tool_description,
                            path_pic,
                            x
                        ]
                        cur.execute(sql,val)
                        connect.commit()
                        return redirect(url_for('ownerproduct_tool'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","danger")
    else:
        return redirect(url_for('home'))

@app.route("/add_decoration", methods=["GET", "POST"])
def add_decoration():
    if session.get("user",None) is not None:
        if request.method=="POST":
            dec_Owner = str(session.get("user"))
            dec_name = str(request.form.get("dec_name"))
            dec_price = request.form.get("dec_price")
            dec_amount = request.form.get("dec_amount")
            dec_description = request.form.get("dec_description")
            x = datetime.datetime.now() 
            if dec_price.isnumeric() and dec_amount.isnumeric():
                if request.files:
                    path_pic = "static\\images\\product_decoration_images\\"+str(uuid.uuid4())+".jpg"
                    print(dec_Owner+" "+dec_name+" "+dec_price+" "+dec_amount+" "+dec_description+" "+path_pic)
                    file = request.files["dec_pic"]
                    filepath = path_pic
                    file.save(filepath)
                    with sqlite3.connect("mydata.db") as connect:
                        cur = connect.cursor()
                        sql = "INSERT INTO accessories_product(accessories_Owner,accessories_Name,accessories_Price,accessories_Amount,accessories_description,accessories_Images,time) VALUES(?,?,?,?,?,?,?)"
                        val = [
                            dec_Owner,
                            dec_name,
                            float(dec_price),
                            int(dec_amount),
                            dec_description,
                            path_pic,
                            x
                        ]
                        cur.execute(sql,val)
                        connect.commit()
                        return redirect(url_for('ownerproduct_accessories'))
            else:
                flash("ราคา หรือ จำนวน ไม่ใช่ตัวเลข","warning")
    else:
        return redirect(url_for('home'))

@app.route("/confirmproduct" , methods=["GET","POST"])
def confirmproduct():
    status = request.form.get("status")
    id = request.form.get("id")
    buyer = request.form.get("buyer")
    sendmailconfirm(buyer,id)
    print('status:id'+ '=' + status + ':' + id)
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "update basket set status = ? where id = ?"
                val = [
                    status,
                    id
                ]
                cur.execute(sql , val)
                connect.commit()
                sql = "update history set status = ? , status_product = ? where id = ?"
                val = [
                    status,
                    'disabled',
                    id
                ]
                cur.execute(sql , val)
                connect.commit()      
                return redirect(url_for("sell_history"))

        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "update basket set status = ? where username = ? and id = ?"
                val = [
                    status,
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                sql = "update history set status = ? , status_product = ? where username = ? and id = ?"
                val = [
                    status,
                    'disabled',
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                connect.commit()
                return redirect(url_for("sell_history"))
    else:
        return redirect(url_for("home"))

@app.route("/cancelproduct" , methods=["GET","POST"])
def cancelproduct():
    status = request.form.get("status")
    id = request.form.get("id")
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                
                sql = "update basket set status = ? where username = ? and id = ?"
                val = [
                    status,
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                sql = "update history set status = ? , status_product = ? where username = ? and id = ?"
                val = [
                    status,
                    'disabled',
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                connect.commit()
                return redirect(url_for("profile"))

        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "update basket set status = ? where username = ? and id = ?"
                val = [
                    status,
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                sql = "update history set status = ? , status_product = ? where username = ? and id = ?"
                val = [
                    status,
                    'disabled',
                    session["user"],
                    id
                ]
                cur.execute(sql , val)
                connect.commit()
                return redirect(url_for("profile"))
    else:
        return redirect(url_for("home"))

@app.route("/upload_slip" , methods=["GET","POST"])
def upload_slip():
    id = request.form.get("id")
    if session.get("user",None) is not None:
        if request.files:
            with sqlite3.connect("mydata.db") as connect:
                x = datetime.datetime.now()
                date = x.strftime("%Y") + x.strftime("%m") + x.strftime("%d")
                time = x.strftime("%H") + x.strftime("%M") + x.strftime("S")
                slip_name = session["user"]+'-'+date+'-'+time
                path_pic = "static\\images\\payment\\"+session["user"]+date+time+id+".jpg"
                file = request.files["slip_pic"]
                filepath = path_pic
                file.save(filepath)
                sendmailslip(id,filepath)
                cur = connect.cursor()
                sql = "UPDATE basket SET status = ?  WHERE username = ? and id = ?"
                val = [
                    'waiting_for_approve',
                    session["user"],
                    id
                ]       
                cur.execute(sql , val)
                sql = "UPDATE history SET status = ? , slip_image = ?  WHERE username = ? and id = ?"
                val = [
                    'waiting_for_approve',
                    path_pic,
                    session["user"],
                    id
                ]       
                cur.execute(sql , val)
                connect.commit()
                return redirect(url_for('buy_history'))
    

@app.route("/pic_profile" , methods=["GET", "POST"])
def pic_profile():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            if request.files:
                with sqlite3.connect("mydata.db") as connect:
                    path_pic = "static\\images\\pic_profile\\"+str(uuid.uuid4())+".jpg"
                    file = request.files["seller_pic"]
                    filepath = path_pic
                    file.save(filepath)
                    cur = connect.cursor()
                    sql = "UPDATE seller SET seller_pic = ?  WHERE seller_ID = ?"
                    val = [
                        path_pic,
                        session["user"]
                    ]                    
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('profile'))
    if session.get("user",None) is not None:
        if session.get("role") == 'user':
            if request.files:
                with sqlite3.connect("mydata.db") as connect:
                    path_pic = "static\\images\\pic_profile\\"+str(uuid.uuid4())+".jpg"
                    file = request.files["user_pic"]
                    filepath = path_pic
                    file.save(filepath)
                    cur = connect.cursor()
                    sql = "UPDATE user SET user_pic = ?  WHERE user_ID = ?"
                    val = [
                        path_pic,
                        session["user"]
                    ]                    
                    cur.execute(sql , val)
                    connect.commit()
                    return redirect(url_for('profile'))

@app.route("/goto_profile_seller_new_session" , methods=["GET", "POST"])
def goto_profile_seller_new_session():
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "select * from seller where seller_ID = ?"
        val = [session['user']]
        cur.execute(sql,val)
        seller_data = cur.fetchall()

        session.pop('user',None)
        session.clear()
        session.pop('user',None)                                    
        session['user'] = seller_data[0][0]
        session['role'] = "seller"

        return redirect(url_for('profile'))

@app.route("/goto_profile_user_new_session")
def goto_profile_user_new_session(username):
    with sqlite3.connect("mydata.db") as connect:
        cur = connect.cursor()
        sql = "select * from user where user_ID = ?"
        val = [username]
        cur.execute(sql,val)
        user_data = cur.fetchall()

        session.pop('user',None)
        session.clear()
        session.pop('user',None)                                    
        session['user'] = user_data[0][0]
        session['role'] = "user"

        return redirect(url_for('profile'))

@app.route("/edit_profile" , methods=["GET", "POST"])
def edit_profile():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            if request.method == "POST":
                username = request.form.get("username")
                firstname = request.form.get("firstname")
                lastname = request.form.get("lastname")
                address = request.form.get("address")
                email = request.form.get("email")
                telephone = request.form.get("telephone")
                line = request.form.get("seller_Line")
                facebook = request.form.get("seller_Facebook")
                storename = request.form.get("seller_Storename")
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    sql = "select seller_Storename from seller where seller_ID = ? and seller_Storename = ?"
                    val = [session.get("user"),storename]
                    cur.execute(sql,val)
                    seller_storename = cur.fetchone()
                    print(seller_storename)
                    if seller_storename is None:
                        if sellerStoreValidate(storename):
                            if session.get("user") == username:
                                sql = "select seller_Email from seller where seller_ID = ? and seller_Email = ?"
                                val = [session.get("user"),email]
                                cur.execute(sql,val)
                                seller_Email = cur.fetchone()
                                print(seller_Email)

                                if seller_Email is None:
                                    print('เปลี่ยนอีเมล')
                                    print(selleremailValidate(email))
                                    if(selleremailValidate(email)):
                                        sql = "update seller set seller_Firstname = ? , seller_Lastname = ? ,seller_Email = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? , seller_Storename = ? where seller_ID = ?"
                                        val = [
                                            firstname,
                                            lastname,
                                            email,
                                            address,
                                            telephone,
                                            line,
                                            facebook,
                                            storename,
                                            session.get('user')
                                        ]
                                        print(val)
                                        cur.execute(sql,val)
                                        connect.commit()
                                        return(redirect(url_for('profile')))
                                    else:
                                        flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                        return(redirect(url_for('profile')))
                                elif seller_Email[0] == email:
                                    print('อีเมลเดิม')
                                    sql = "update seller set seller_Firstname = ? , seller_Lastname = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? , seller_Storename = ? where seller_ID = ?"                            
                                    val = [
                                        firstname,
                                        lastname,
                                        address,
                                        telephone,
                                        line,
                                        facebook,
                                        storename,
                                        session.get('user')
                                    ]
                                    print(val)
                                    cur.execute(sql,val)
                                    connect.commit()
                                    return(redirect(url_for('profile')))
                            else:
                                if selleridValidate(username):
                                    sql = "select seller_Email from seller where seller_ID = ? and seller_Email = ?"
                                    val = [session.get("user"),email]
                                    cur.execute(sql,val)
                                    seller_Email = cur.fetchone()
                                    print(seller_Email)

                                    if seller_Email is None:
                                        print('เปลี่ยนอีเมล')
                                        print(selleremailValidate(email))
                                        if(selleremailValidate(email)):
                                            sql = "update seller set seller_ID = ? , seller_Firstname = ? , seller_Lastname = ? ,seller_Email = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? , seller_Storename = ? where seller_ID = ?"
                                            val = [
                                                username,
                                                firstname,
                                                lastname,
                                                email,
                                                address,
                                                telephone,
                                                session.get('user')
                                            ]
                                            print(val)
                                            cur.execute(sql,val)
                                            connect.commit()
                                            goto_profile_seller_new_session(username)
                                            return(redirect(url_for('profile')))
                                        else:
                                            flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                            return(redirect(url_for('profile')))
                                    elif seller_Email[0] == email:
                                            print('อีเมลเดิม')
                                            sql = "update seller set seller_ID = ?,seller_Firstname = ? , seller_Lastname = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? , seller_Storename = ? where seller_ID = ?"                            
                                            val = [
                                                username,
                                                firstname,
                                                lastname,
                                                address,
                                                telephone,
                                                session.get('user')
                                            ]
                                            print(val)
                                            cur.execute(sql,val)
                                            connect.commit()
                                            goto_profile_seller_new_session(username)
                                            return(redirect(url_for('profile')))
                                else:
                                    flash("ชื่อผู้ใช้งานนี้ได้สมัครสมาชิกแล้ว","danger")
                                    return redirect(url_for('profile'))
                        else:
                            flash("ชื่อร้านค้าได้ลงทะเบียนแล้ว","danger")
                            return redirect(url_for('profile'))
                    elif storename == seller_storename[0]:
                        if session.get("user") == username:
                            sql = "select seller_Email from seller where seller_ID = ? and seller_Email = ?"
                            val = [session.get("user"),email]
                            cur.execute(sql,val)
                            seller_Email = cur.fetchone()
                            print(seller_Email)

                            if seller_Email is None:
                                print('เปลี่ยนอีเมล')
                                print(selleremailValidate(email))
                                if(selleremailValidate(email)):
                                    sql = "update seller set seller_Firstname = ? , seller_Lastname = ? ,seller_Email = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? where seller_ID = ?"
                                    val = [
                                        firstname,
                                        lastname,
                                        email,
                                        address,
                                        telephone,
                                        line,
                                        facebook,
                                        session.get('user')
                                    ]
                                    print(val)
                                    cur.execute(sql,val)
                                    connect.commit()
                                    return(redirect(url_for('profile')))
                                else:
                                    flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                    return(redirect(url_for('profile')))
                            elif seller_Email[0] == email:
                                print('อีเมลเดิม')
                                sql = "update seller set seller_Firstname = ? , seller_Lastname = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? where seller_ID = ?"                            
                                val = [
                                    firstname,
                                    lastname,
                                    address,
                                    telephone,
                                    line,
                                    facebook,
                                    session.get('user')
                                ]
                                print(val)
                                cur.execute(sql,val)
                                connect.commit()
                                return(redirect(url_for('profile')))
                        else:
                            if selleridValidate(username):
                                sql = "select seller_Email from seller where seller_ID = ? and seller_Email = ?"
                                val = [session.get("user"),email]
                                cur.execute(sql,val)
                                seller_Email = cur.fetchone()
                                print(seller_Email)

                                if seller_Email is None:
                                    print('เปลี่ยนอีเมล')
                                    print(selleremailValidate(email))
                                    if(selleremailValidate(email)):
                                        sql = "update seller set seller_ID = ? , seller_Firstname = ? , seller_Lastname = ? ,seller_Email = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? where seller_ID = ?"
                                        val = [
                                            username,
                                            firstname,
                                            lastname,
                                            email,
                                            address,
                                            telephone,
                                            line,
                                            facebook,
                                            session.get('user')
                                        ]
                                        print(val)
                                        cur.execute(sql,val)
                                        connect.commit()
                                        goto_profile_seller_new_session(username)
                                        return(redirect(url_for('profile')))
                                    else:
                                        flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                        return(redirect(url_for('profile')))
                                elif seller_Email[0] == email:
                                        print('อีเมลเดิม')
                                        sql = "update seller set seller_ID = ?,seller_Firstname = ? , seller_Lastname = ? ,seller_Telephone = ? , seller_Address = ? , seller_Line = ? , seller_Facebook = ? where seller_ID = ?"                            
                                        val = [
                                            username,
                                            firstname,
                                            lastname,
                                            address,
                                            telephone,
                                            line,
                                            facebook,
                                            session.get('user')
                                        ]
                                        print(val)
                                        cur.execute(sql,val)
                                        connect.commit()
                                        goto_profile_seller_new_session(username)
                                        return(redirect(url_for('profile')))
                            else:
                                flash("ชื่อผู้ใช้งานนี้ได้สมัครสมาชิกแล้ว","danger")
                                return redirect(url_for('profile'))
                            return redirect(url_for('profile'))

        if session.get("role") == 'user':
            if request.method == "POST":
                username = request.form.get("username")
                firstname = request.form.get("firstname")
                lastname = request.form.get("lastname")
                address = request.form.get("address")
                email = request.form.get("email")
                telephone = request.form.get("telephone")
                print(session)
                if session.get("user") == username:
                    with sqlite3.connect("mydata.db") as connect:
                        cur = connect.cursor()
                        sql = "select user_Email from user where user_ID = ? and user_Email = ?"
                        val = [session.get("user"),email]
                        cur.execute(sql,val)
                        user_Email = cur.fetchone()
                        print(user_Email)

                        if user_Email is None:
                            print('เปลี่ยนอีเมล')
                            print(useremailValidate(email))
                            if(useremailValidate(email)):
                                sql = "update user set user_Firstname = ? , user_Lastname = ? ,user_Email = ? ,user_Telephone = ? , user_Address = ? where user_ID = ?"
                                val = [
                                    firstname,
                                    lastname,
                                    email,
                                    address,
                                    telephone,
                                    session.get('user')
                                ]
                                print(val)
                                cur.execute(sql,val)
                                connect.commit()
                                return(redirect(url_for('profile')))
                            else:
                                flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                return(redirect(url_for('profile')))
                        elif user_Email[0] == email:
                            print('อีเมลเดิม')
                            sql = "update user set user_Firstname = ? , user_Lastname = ? ,user_Telephone = ? , user_Address = ? where user_ID = ?"
                            val = [
                                firstname,
                                lastname,
                                address,
                                telephone,
                                session.get('user')
                            ]
                            print(val)
                            cur.execute(sql,val)
                            connect.commit()
                            return(redirect(url_for('profile')))
                else:
                    if useridValidate(username):
                        with sqlite3.connect("mydata.db") as connect:
                            cur = connect.cursor()
                            sql = "select user_Email from user where user_ID = ? and user_Email = ?"
                            val = [session.get("user"),email]
                            cur.execute(sql,val)
                            user_Email = cur.fetchone()
                            print(user_Email)

                            if user_Email is None:
                                print('เปลี่ยนอีเมล')
                                print(useremailValidate(email))
                                if(useremailValidate(email)):
                                    sql = "update user set user_ID = ?, user_Firstname = ? , user_Lastname = ? ,user_Email = ? ,user_Telephone = ? , user_Address = ? where user_ID = ?"
                                    val = [
                                        username,
                                        firstname,
                                        lastname,
                                        email,
                                        address,
                                        telephone,
                                        session.get('user')
                                    ]
                                    print(val)
                                    cur.execute(sql,val)
                                    connect.commit()
                                    goto_profile_user_new_session(username)
                                    return(redirect(url_for('profile')))
                                else:
                                    flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                                    return(redirect(url_for('profile')))
                            elif user_Email[0] == email:
                                print('อีเมลเดิม')
                                sql = "update user set user_ID = ?, user_Firstname = ? , user_Lastname = ? ,user_Telephone = ? , user_Address = ? where user_ID = ?"
                                val = [
                                    username,
                                    firstname,
                                    lastname,
                                    address,
                                    telephone,
                                    session.get('user')
                                ]
                                print(val)
                                cur.execute(sql,val)
                                connect.commit()
                                goto_profile_user_new_session(username)
                                return(redirect(url_for('profile')))
                    else:
                        flash("ชื่อผู้ใช้งานนี้ได้สมัครสมาชิกแล้ว","danger")
                        return redirect(url_for('profile'))
                return redirect(url_for('profile'))

@app.route("/change_password" , methods=["GET", "POST"])
def change_password():
    if session.get("user",None) is not None:
        if request.method == "POST":
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                old_password = request.form.get('old_password')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                secure_password = sha256_crypt.encrypt(str(password))
                request_password = ''
                print(password)
                print(confirm_password)
                print(old_password)
                if session.get("role") == 'seller':
                    sql = "select seller_Password from seller where seller_ID = ?"
                    val = [session['user']]
                    cur.execute(sql,val)
                    request_password = cur.fetchone()[0]
                if session.get("role") == 'user':
                    sql = "select user_Password from user where user_ID = ?"
                    val = [session['user']]
                    cur.execute(sql,val)
                    request_password = cur.fetchone()[0]
                
                if(sha256_crypt.verify(old_password, request_password)):
                    if password == confirm_password:
                        sql = "update seller set seller_Password = ? where seller_ID = ?"
                        val = [secure_password , session['user']]
                        cur.execute(sql,val)
                        connect.commit()
                        return redirect(url_for('profile'))
                    else:
                        flash("กรอกรหัสเก่าให้ถูกต้อง","danger")
                        return redirect(url_for('profile'))
                else:
                    flash("กรอกรหัสเก่าให้ถูกต้อง","danger")
                    return redirect(url_for('profile'))

            


@app.route("/fish_product_search", methods=["GET", "POST"])
def fish_product_search():
    if request.method=="POST":
        search=request.form['search']
        if session.get("user",None) is not None:
            if session.get("role") == 'seller': 
                with sqlite3.connect("mydata.db") as connect:                
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM fish_product WHERE fish_Name LIKE ?",['%'+search+'%'])
                    fish_product = cur.fetchall()
                    return render_template("product_fish_seller.html",fish=fish_product, seller = session['user'])               
            if session.get("role") == 'user':           
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM fish_product WHERE fish_Name LIKE ?",['%'+search+'%'])
                    fish_product = cur.fetchall()
                    return render_template("product_fish_user.html",fish=fish_product, user = session['user'])               
        else:
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT * FROM fish_product WHERE fish_Name LIKE ?",['%'+search+'%'])
                fish_product = cur.fetchall()
                return render_template("product_fish.html",fish=fish_product)
        return redirect(url_for('fish_product'))

@app.route("/accessories_product_search", methods=["GET", "POST"])
def accessories_product_search():
    if request.method=="POST":
        search=request.form['search']
        if session.get("user",None) is not None:
            if session.get("role") == 'seller': 
                with sqlite3.connect("mydata.db") as connect:                
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM accessories_product WHERE accessories_Name LIKE ?",['%'+search+'%'])
                    accessories_product = cur.fetchall()
                    return render_template("product_accessories_seller.html",accessories=accessories_product, seller = session['user'])               
            if session.get("role") == 'user':           
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM accessories_product WHERE accessories_Name LIKE ?",['%'+search+'%'])
                    accessories_product = cur.fetchall()
                    return render_template("product_accessories_user.html",accessories=accessories_product, user = session['user'])               
        else:
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT * FROM accessories_product WHERE accessories_Name LIKE ?",['%'+search+'%'])
                accessories_product = cur.fetchall()
                return render_template("product_accessories.html",accessories=accessories_product)  
    return redirect(url_for('accessories_product')) 

@app.route("/tool_product_search", methods=["GET", "POST"])
def tool_product_search():
    if request.method=="POST":
        search=request.form['search']
        if session.get("user",None) is not None:
            if session.get("role") == 'seller': 
                with sqlite3.connect("mydata.db") as connect:                
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM tool_product WHERE tool_Name LIKE ?",['%'+search+'%'])
                    tool_product = cur.fetchall()
                    return render_template("product_tool_seller.html",tool=tool_product, seller = session['user'])               
            if session.get("role") == 'user':           
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    cur.execute("SELECT * FROM tool_product WHERE tool_Name LIKE ?",['%'+search+'%'])
                    tool_product = cur.fetchall()
                    return render_template("product_tool_user.html",tool=tool_product, user = session['user'])               
        else:
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT * FROM tool_product WHERE tool_Name LIKE ?",['%'+search+'%'])
                tool_product = cur.fetchall()
                return render_template("product_tool.html",tool=tool_product)
        return redirect(url_for('tool_product'))
########################Template########################
@app.route("/")
def home():
    print(session)
    print(session.get("user"))
    print(session.get("role"))
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller")
                seller = cur.fetchall()
                cur.execute("select fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc limit 3")
                search_count = cur.fetchall()
                # cur.execute("SELECT fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID WHERE fish_ID = (SELECT MAX(fish_ID) from fish_product)")
                cur.execute("SELECT fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by time desc limit 5")
                lastest_product = cur.fetchall()
                return render_template("home_seller.html",seller_data=seller,search_count=search_count,lastest_product=lastest_product,seller = session['user'])
        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller")
                seller = cur.fetchall()
                cur.execute("select fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc limit 3")
                search_count = cur.fetchall()
                cur.execute("SELECT fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by time desc limit 5")
                lastest_product = cur.fetchall()
                return render_template("home_user.html",seller_data=seller,search_count=search_count,lastest_product=lastest_product,user = session['user'])
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("select * from seller")
            seller = cur.fetchall()
            cur.execute("select fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc limit 3")
            search_count = cur.fetchall()
            cur.execute("SELECT fish_product.* , seller.seller_Storename from fish_product inner join seller on fish_product.fish_Owner = seller.seller_ID order by time desc limit 5")
            lastest_product = cur.fetchall()
            return render_template("index.html",seller_data=seller,search_count=search_count,lastest_product=lastest_product)

@app.route("/fish_product")
def fish_product():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:                
                cur = connect.cursor()
                cur.execute("SELECT fish_product.*, seller.seller_Storename FROM seller INNER JOIN fish_product ON fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc;")
                fish_product = cur.fetchall()
                for i in range(len(fish_product)):
                    fish_product[i] = list(fish_product[i])
                    fish_product[i][3] = str('{:,.2f}'.format(fish_product[i][3]))
                    fish_product[i][4] = str('{:,}'.format(int(fish_product[i][4])))
                    fish_product[i] = tuple(fish_product[i])
                return render_template("product_fish_seller.html",fish=fish_product, seller = session['user'])               
        if session.get("role") == 'user':           
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT fish_product.*, seller.seller_Storename FROM seller INNER JOIN fish_product ON fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc;")
                fish_product = cur.fetchall()
                for i in range(len(fish_product)):
                    fish_product[i] = list(fish_product[i])
                    fish_product[i][3] = str('{:,.2f}'.format(fish_product[i][3]))
                    fish_product[i][4] = str('{:,}'.format(int(fish_product[i][4])))
                    fish_product[i] = tuple(fish_product[i])
                return render_template("product_fish_user.html",fish=fish_product, user = session['user'])               
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("SELECT fish_product.*, seller.seller_Storename FROM seller INNER JOIN fish_product ON fish_product.fish_Owner = seller.seller_ID order by fish_select_count desc;")
            fish_product = cur.fetchall()
            for i in range(len(fish_product)):
                fish_product[i] = list(fish_product[i])
                fish_product[i][3] = str('{:,.2f}'.format(fish_product[i][3]))
                fish_product[i][4] = str('{:,}'.format(int(fish_product[i][4])))
                fish_product[i] = tuple(fish_product[i])
            return render_template("product_fish.html",fish=fish_product)

@app.route("/accessories_product")
def accessories_product():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:                
                cur = connect.cursor()
                cur.execute("SELECT accessories_product.*, seller.seller_Storename FROM seller INNER JOIN accessories_product ON accessories_product.accessories_Owner = seller.seller_ID order by time desc;")
                accessories_product = cur.fetchall()
                for i in range(len(accessories_product)):
                    accessories_product[i] = list(accessories_product[i])
                    accessories_product[i][2] = str('{:,.2f}'.format(accessories_product[i][2]))
                    accessories_product[i][3] = str('{:,}'.format(int(accessories_product[i][3])))
                    accessories_product[i] = tuple(accessories_product[i])
                return render_template("product_accessories_seller.html",accessories=accessories_product, seller = session['user'])               
        if session.get("role") == 'user':           
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT accessories_product.*, seller.seller_Storename FROM seller INNER JOIN accessories_product ON accessories_product.accessories_Owner = seller.seller_ID order by time desc;")
                accessories_product = cur.fetchall()
                for i in range(len(accessories_product)):
                    accessories_product[i] = list(accessories_product[i])
                    accessories_product[i][2] = str('{:,.2f}'.format(accessories_product[i][2]))
                    accessories_product[i][3] = str('{:,}'.format(int(accessories_product[i][3])))
                    accessories_product[i] = tuple(accessories_product[i])
                return render_template("product_accessories_user.html",accessories=accessories_product, user = session['user'])               
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("SELECT accessories_product.*, seller.seller_Storename FROM seller INNER JOIN accessories_product ON accessories_product.accessories_Owner = seller.seller_ID order by time desc;")
            accessories_product = cur.fetchall()
            for i in range(len(accessories_product)):
                accessories_product[i] = list(accessories_product[i])
                accessories_product[i][2] = str('{:,.2f}'.format(accessories_product[i][2]))
                accessories_product[i][3] = str('{:,}'.format(int(accessories_product[i][3])))
                accessories_product[i] = tuple(accessories_product[i])
            return render_template("product_accessories.html",accessories=accessories_product)  

@app.route("/tool_product")
def tool_product():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:                
                cur = connect.cursor()
                cur.execute("SELECT tool_product.*, seller.seller_Storename FROM seller INNER JOIN tool_product ON tool_product.tool_Owner = seller.seller_ID order by time desc;")
                tool_product = cur.fetchall()
                for i in range(len(tool_product)):
                    tool_product[i] = list(tool_product[i])
                    tool_product[i][2] = str('{:,.2f}'.format(tool_product[i][2]))
                    tool_product[i][3] = str('{:,}'.format(int(tool_product[i][3])))
                    tool_product[i] = tuple(tool_product[i])
                return render_template(
                    "product_tool_seller.html",
                    tool=tool_product, 
                    seller = session['user']
                )               
        if session.get("role") == 'user':           
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("SELECT tool_product.*, seller.seller_Storename FROM seller INNER JOIN tool_product ON tool_product.tool_Owner = seller.seller_ID order by time desc;")
                tool_product = cur.fetchall()
                tool_list = []
                for i in range(len(tool_product)):
                    tool_product[i] = list(tool_product[i])
                    tool_product[i][2] = str('{:,.2f}'.format(tool_product[i][2]))
                    tool_product[i][3] = str('{:,}'.format(int(tool_product[i][3])))
                    tool_product[i] = tuple(tool_product[i])

                return render_template("product_tool_user.html",tool=tool_product, user = session['user'])               
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("SELECT tool_product.*, seller.seller_Storename FROM seller INNER JOIN tool_product ON tool_product.tool_Owner = seller.seller_ID order by time desc;")
            tool_product = cur.fetchall()
            for i in range(len(tool_product)):
                tool_product[i] = list(tool_product[i])
                tool_product[i][2] = str('{:,.2f}'.format(tool_product[i][2]))
                tool_product[i][3] = str('{:,}'.format(int(tool_product[i][3])))
                tool_product[i] = tuple(tool_product[i])
            return render_template("product_tool.html",tool=tool_product)

@app.route("/shop_fish/<string:id_data>", methods=["GET", "POST"])
def shop_fish(id_data):
    SellerID = id_data
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()
                cur.execute('select count(*) from fish_product where fish_Owner = ?',[SellerID])
                fish_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM fish_product where fish_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                fishproduct_data = cur.fetchall() 
                fish_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=fish_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(fishproduct_data)):
                    fishproduct_data[i] = list(fishproduct_data[i])
                    fishproduct_data[i][3] = str('{:,.2f}'.format(fishproduct_data[i][3]))
                    fishproduct_data[i][4] = str('{:,}'.format(int(fishproduct_data[i][4])))
                    fishproduct_data[i] = tuple(fishproduct_data[i])

                return render_template(
                    "shop_fish_seller.html",
                    fish_pagination=fish_pagination,
                    seller_shop=seller[0], 
                    fishproduct_data=fishproduct_data, 
                    seller = session['user']
                )          

        if session.get("role") == 'user': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute('select count(*) from fish_product where fish_Owner = ?',[SellerID])
                fish_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM fish_product where fish_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                fishproduct_data = cur.fetchall() 
                fish_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=fish_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(fishproduct_data)):
                    fishproduct_data[i] = list(fishproduct_data[i])
                    fishproduct_data[i][3] = str('{:,.2f}'.format(fishproduct_data[i][3]))
                    fishproduct_data[i][4] = str('{:,}'.format(int(fishproduct_data[i][4])))
                    fishproduct_data[i] = tuple(fishproduct_data[i])

                return render_template(
                    "shop_fish_user.html",
                    fish_pagination=fish_pagination,
                    seller_shop=seller[0], 
                    fishproduct_data=fishproduct_data, 
                    user = session['user']
                )                      
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("select * from seller where seller_id = ?",[SellerID])
            seller = cur.fetchall()
            print(seller)
            cur.execute('select count(*) from fish_product where fish_Owner = ?',[SellerID])
            fish_total = cur.fetchone()[0]
            page, per_page, offset = get_page_args(page_parameter='page')
            per_page = 12
            if offset != 0:
                offset = offset + 2
            sql = "SELECT * FROM fish_product where fish_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
            val = [SellerID,per_page, offset]
            cur.execute(sql,val)
            fishproduct_data = cur.fetchall() 
            fish_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=fish_total,
                css_framework='bootstrap4'
            )

            for i in range(len(fishproduct_data)):
                fishproduct_data[i] = list(fishproduct_data[i])
                fishproduct_data[i][3] = str('{:,.2f}'.format(fishproduct_data[i][3]))
                fishproduct_data[i][4] = str('{:,}'.format(int(fishproduct_data[i][4])))
                fishproduct_data[i] = tuple(fishproduct_data[i])

            return render_template(
                "shop_fish.html",
                fish_pagination=fish_pagination,
                seller_shop=seller[0], 
                fishproduct_data=fishproduct_data, 
            )    

@app.route("/shop_accessories/<string:id_data>", methods=["GET", "POST"])
def shop_accessories(id_data):
    SellerID = id_data
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from accessories_product where accessories_Owner = ?",[SellerID])
                accessories_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM accessories_product where accessories_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                accessoriesproduct_data = cur.fetchall() 
                accessories_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=accessories_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(accessoriesproduct_data)):
                    accessoriesproduct_data[i] = list(accessoriesproduct_data[i])
                    accessoriesproduct_data[i][2] = str('{:,.2f}'.format(accessoriesproduct_data[i][2]))
                    accessoriesproduct_data[i][3] = str('{:,}'.format(int(accessoriesproduct_data[i][3])))
                    accessoriesproduct_data[i] = tuple(accessoriesproduct_data[i])

                return render_template(
                    "shop_accessories_seller.html",
                    accessories_pagination=accessories_pagination,
                    seller_shop=seller[0], 
                    accessoriesproduct_data=accessoriesproduct_data, 
                    seller = session['user']
                )                      

        if session.get("role") == 'user': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from accessories_product where accessories_Owner = ?",[SellerID])
                accessories_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM accessories_product where accessories_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                accessoriesproduct_data = cur.fetchall() 
                accessories_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=accessories_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(accessoriesproduct_data)):
                    accessoriesproduct_data[i] = list(accessoriesproduct_data[i])
                    accessoriesproduct_data[i][2] = str('{:,.2f}'.format(accessoriesproduct_data[i][2]))
                    accessoriesproduct_data[i][3] = str('{:,}'.format(int(accessoriesproduct_data[i][3])))
                    accessoriesproduct_data[i] = tuple(accessoriesproduct_data[i])

                return render_template(
                    "shop_accessories_user.html",
                    accessories_pagination=accessories_pagination,
                    seller_shop=seller[0], 
                    accessoriesproduct_data=accessoriesproduct_data, 
                    user = session['user']
                )                      
    else:
        with sqlite3.connect("mydata.db") as connect:
            
            cur = connect.cursor()
            cur.execute("select * from seller where seller_id = ?",[SellerID])
            seller = cur.fetchall()

            cur.execute("select count(*) from accessories_product where accessories_Owner = ?",[SellerID])
            accessories_total = cur.fetchone()[0]
            page, per_page, offset = get_page_args(page_parameter='page')
            per_page = 12
            if offset != 0:
                offset = offset + 2
            sql = "SELECT * FROM accessories_product where accessories_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
            val = [SellerID,per_page, offset]
            cur.execute(sql,val)
            accessoriesproduct_data = cur.fetchall() 
            accessories_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=accessories_total,
                css_framework='bootstrap4'
            )

            for i in range(len(accessoriesproduct_data)):
                accessoriesproduct_data[i] = list(accessoriesproduct_data[i])
                accessoriesproduct_data[i][2] = str('{:,.2f}'.format(accessoriesproduct_data[i][2]))
                accessoriesproduct_data[i][3] = str('{:,}'.format(int(accessoriesproduct_data[i][3])))
                accessoriesproduct_data[i] = tuple(accessoriesproduct_data[i])

            return render_template(
                "shop_accessories.html",
                accessories_pagination=accessories_pagination,
                seller_shop=seller[0], 
                accessoriesproduct_data=accessoriesproduct_data, 
            )    

@app.route("/shop_tool/<string:id_data>", methods=["GET", "POST"])
def shop_tool(id_data):
    SellerID = id_data
    if session.get("user",None) is not None:
        if session.get("role") == 'seller': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from tool_product where tool_Owner = ?",[SellerID])
                tool_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM tool_product where tool_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                toolproduct_data = cur.fetchall() 
                tool_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=tool_total,
                    css_framework='bootstrap4'
                )

                return render_template(
                    "shop_tool_seller.html",
                    tool_pagination=tool_pagination,
                    seller_shop=seller[0], 
                    toolproduct_data=toolproduct_data,
                    seller = session['user']
                )                      

        if session.get("role") == 'user': 
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from tool_product where tool_Owner = ?",[SellerID])
                tool_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM tool_product where tool_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                toolproduct_data = cur.fetchall() 
                tool_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=tool_total,
                    css_framework='bootstrap4'
                )

                return render_template(
                    "shop_tool_user.html",
                    tool_pagination=tool_pagination,
                    seller_shop=seller[0], 
                    toolproduct_data=toolproduct_data,
                    user = session['user']
                )                      
    else:
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("select * from seller where seller_id = ?",[SellerID])
            seller = cur.fetchall()

            cur.execute("select count(*) from tool_product where tool_Owner = ?",[SellerID])
            tool_total = cur.fetchone()[0]
            page, per_page, offset = get_page_args(page_parameter='page')
            per_page = 12
            if offset != 0:
                offset = offset + 2
            sql = "SELECT * FROM tool_product where tool_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
            val = [SellerID,per_page, offset]
            cur.execute(sql,val)
            toolproduct_data = cur.fetchall() 
            tool_pagination = Pagination(
                page=page,
                per_page=per_page,
                total=tool_total,
                css_framework='bootstrap4'
            )

            for i in range(len(toolproduct_data)):
                toolproduct_data[i] = list(toolproduct_data[i])
                toolproduct_data[i][2] = str('{:,.2f}'.format(toolproduct_data[i][2]))
                toolproduct_data[i][3] = str('{:,}'.format(int(toolproduct_data[i][3])))
                toolproduct_data[i] = tuple(toolproduct_data[i])

            return render_template(
                "shop_tool.html",
                tool_pagination=tool_pagination,
                seller_shop=seller[0], 
                toolproduct_data=toolproduct_data
            )     

@app.route("/basket", methods=["GET", "POST"])
def basket():
    if session.get("user",None) is not None:
        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                UserID = session['user']
                cur = connect.cursor()
                total = 0
                cur.execute("select * from basket where username = ? and status = ?",[UserID , 'in-cart'])
                basket = cur.fetchall()
                for i in range(len(basket)):                   
                    total = total + float(basket[i][3]*basket[i][5])
                total = str('{:,.2f}'.format(total))
                for i in range(len(basket)):
                    basket[i] = list(basket[i])
                    basket[i][3] = str('{:,.2f}'.format(basket[i][3]))
                    basket[i] = tuple(basket[i])
                return render_template("basket_user.html",basket=basket,user = session['user'],total=total)
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                SellerID = session['user']
                cur = connect.cursor()
                total = 0
                cur.execute("select * from basket where username = ? and status = ?",[SellerID , 'in-cart'])
                
                basket = cur.fetchall()

                for i in range(len(basket)):                   
                    total = total + (basket[i][3]*basket[i][5])
                total = str('{:,.2f}'.format(total))
                
                for i in range(len(basket)):
                    basket[i] = list(basket[i])
                    basket[i][3] = str('{:,.2f}'.format(basket[i][3]))
                    basket[i] = tuple(basket[i])

                return render_template("basket_seller.html",basket=basket,seller = session['user'],total=total)
    else:
        return redirect(url_for("alert"))

@app.route("/fishclassification_search")
def fishclassification_search():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            return render_template("fishclassification_seller.html",seller = session['user'])
        if session.get("role") == 'user':
            return render_template("fishclassification_user.html",user = session['user'])
    else:
        return render_template("fishclassification.html")

@app.route("/register_user" , methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        secure_password = sha256_crypt.encrypt(str(password))
        if useridValidate(username):
            if useremailValidate(email):
                if len(password) >= 6:
                    if password == password_confirm:
                        with sqlite3.connect("mydata.db") as connect:
                            cur = connect.cursor()
                            sql = "INSERT INTO user(user_ID,user_Firstname,user_Lastname,user_Address,user_Email,user_Telephone,user_Password) VALUES(?,?,?,?,?,?,?)"
                            val = [
                                username,
                                firstname,
                                lastname,
                                address,
                                email,
                                phone,
                                secure_password
                            ]
                            cur.execute(sql , val)
                            connect.commit()
                            return redirect(url_for("login_user"))
                    else:
                        flash("รหัสผ่านไม่ตรงกับที่ยืนยัน","danger")
                        return render_template("register_user.html")
                else:
                    flash("ใส่รหัสผ่าน 6 ตัวขึ้นไป","danger")
                    return render_template("register_user.html")
            else:
                flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                return render_template("register_user.html")
        else:
            flash("ชื่อผู้ใช้งานนี้ได้สมัครสมาชิกแล้ว","danger")
            return render_template("register_user.html")
    return render_template("register_user.html")

@app.route("/register_seller" , methods=["GET", "POST"])
def register_seller():
    if request.method == "POST":
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        email = request.form.get("email")
        phone = request.form.get("phone")
        store_name = request.form.get("Store_name")
        line = request.form.get("Line")
        facebook = request.form.get("Facebook")
        # if(line == ""):
        #     line = 'กดแก้ไข้อมูลเพิ่อเพิ่มเติม'
        # if(facebook == ""):
        #     facebook = 'กดแก้ไข้อมูลเพิ่อเพิ่มเติม'
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        secure_password = sha256_crypt.encrypt(str(password))
        print(username+","+firstname+","+address+","+email+","+phone+","+store_name+","+line+","+facebook+","+password+","+password_confirm+","+secure_password)
        if selleridValidate(username):
            if selleremailValidate(email):
                if len(password) >= 6:
                    if password == password_confirm:
                        with sqlite3.connect("mydata.db") as connect:
                            cur = connect.cursor()
                            sql = "INSERT INTO seller(seller_ID,seller_Firstname,seller_Lastname,seller_Email,seller_Telephone,seller_Address,seller_Password,seller_Storename,seller_Line,seller_Facebook) VALUES(?,?,?,?,?,?,?,?,?,?)"
                            val = [
                                username,
                                firstname,
                                lastname,
                                email,
                                phone,
                                address,
                                secure_password,
                                store_name,
                                line,
                                facebook
                            ]
                            cur.execute(sql , val)
                            connect.commit()
                            return redirect(url_for("login_seller"))
                    else:
                        flash("รหัสผ่านไม่ตรงกับที่ยืนยัน","danger")
                        return render_template("register_seller.html")
                else:
                    flash("ใส่รหัสผ่าน 6 ตัวขึ้นไป","danger")
                    return render_template("register_seller.html")
            else:
                flash("อีเมลนี้ได้สมัครสมาชิกแล้ว","danger")
                return render_template("register_seller.html")
        else:
            flash("ชื่อผู้ใช้งานนี้ได้สมัครสมาชิกแล้ว","danger")
            return render_template("register_seller.html")
    return render_template("register_seller.html")

@app.route("/login_seller",methods=["GET","POST"])
def login_seller():
    if request.method == "POST":
        session.pop('user',None)
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("SELECT * FROM seller WHERE seller_ID = ?" , [username])
            get_user = cur.fetchall()
            if not get_user:
                flash("ไม่พบผู้ใช้งาน","danger")
            else:
                get_password = get_user[0][8]
                if(sha256_crypt.verify(password, get_password)):
                    if get_user[0][12] == 'danger':
                        flash("บัญชีนี้ปิดการใช้บริการ","danger")
                    else:
                        session['user'] = request.form['username']
                        session['role'] = "seller"
                        return redirect(url_for('home'))
                else:
                    flash("รหัสผ่าน หรือ ชื่อผู้ใช้งานไม่ถูกต้อง","warning")
    return render_template("login_seller.html")

@app.route("/login_user",methods=["GET","POST"])
def login_user():
    if request.method == "POST":
        session.pop('user',None)
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect("mydata.db") as connect:
            cur = connect.cursor()
            cur.execute("SELECT * FROM user WHERE user_ID = ?" , [username])
            get_user = cur.fetchall()
            if not get_user:
                flash("ไม่พบผู้ใช้งาน","danger")
            else:
                get_password = get_user[0][6]
                if(sha256_crypt.verify(password, get_password)):
                    session['user'] = request.form['username']
                    session['role'] = "user"
                    return redirect(url_for('home'))
                    # flash("Login success","success")
                else:
                    flash("รหัสผ่าน หรือ อีเมลไม่ถูกต้อง","warning")
    return render_template("login_user.html")

@app.route("/profile" , methods=["GET", "POST"])
def profile():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "select seller_ID , seller_Firstname , seller_Lastname , seller_Email , seller_Telephone , seller_Address , seller_Line , seller_Facebook , seller_Storename , seller_pic from seller where seller_ID = ?"
                val = [session['user']]
                cur.execute(sql,val)
                seller_data = cur.fetchall()

                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )
                sql = "SELECT * FROM history where username = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [session['user'],'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_buy_data = cur.fetchall()
                history_buy_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(history_buy_data),
                    css_framework='bootstrap4'
                )

                for i in range(len(history_buy_data)):
                    history_buy_data[i] = list(history_buy_data[i])
                    history_buy_data[i][3] = str('{:,.2f}'.format(history_buy_data[i][3]*history_buy_data[i][5]))
                    if history_buy_data[i][8] == 'waiting':
                        history_buy_data[i][8] = str('รอการชำระเงิน')
                    if history_buy_data[i][8] == 'waiting_for_approve':
                        history_buy_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'cancel':
                        history_buy_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'confirm':
                        history_buy_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_buy_data[i] = tuple(history_buy_data[i])

                shop_name = seller_data[0][8]
                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )
                sql = "SELECT * FROM history where shop = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [shop_name,'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_sell_data = cur.fetchall()
                history_sell_pagination= Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(history_sell_data),
                    css_framework='bootstrap4'
                )

                for i in range(len(history_sell_data)):
                    history_sell_data[i] = list(history_sell_data[i])
                    history_sell_data[i][3] = str('{:,.2f}'.format(history_sell_data[i][3]*history_sell_data[i][5]))
                    if history_sell_data[i][8] == 'waiting':
                        history_sell_data[i][8] = str('รอการชำระเงิน')
                    if history_sell_data[i][8] == 'waiting_for_approve':
                        history_sell_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_sell_data[i][8] == 'cancel':
                        history_sell_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_sell_data[i][8] == 'confirm':
                        history_sell_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_sell_data[i] = tuple(history_sell_data[i])

                return render_template(
                    "profile_seller.html",
                    seller_data = seller_data[0],
                    history_buy_pagination = history_buy_pagination,
                    history_buy_data = history_buy_data,
                    history_sell_pagination = history_sell_pagination,
                    history_sell_data = history_sell_data,
                    seller = session['user']
                )

        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "select user_ID , user_Firstname , user_Lastname , user_Email , user_Telephone , user_Address , user_pic from user where user_ID = ?"
                val = [session['user']]
                cur.execute(sql,val)
                user_data = cur.fetchall()
                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )
                sql = "SELECT * FROM history where username = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [session['user'],'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_buy_data = cur.fetchall()
                history_buy_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(history_buy_data),
                    css_framework='bootstrap4'
                )

                # sql = "select * from history where username = ? and status is not ?"
                # val = [session['user'],'in-cart']
                # cur.execute(sql,val)
                # history_buy_data = cur.fetchall()

                for i in range(len(history_buy_data)):
                    history_buy_data[i] = list(history_buy_data[i])
                    history_buy_data[i][3] = str('{:,.2f}'.format(history_buy_data[i][3]*history_buy_data[i][5]))
                    if history_buy_data[i][8] == 'waiting':
                        history_buy_data[i][8] = str('รอการชำระเงิน')
                    if history_buy_data[i][8] == 'waiting_for_approve':
                        history_buy_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'cancel':
                        history_buy_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'confirm':
                        history_buy_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_buy_data[i] = tuple(history_buy_data[i])

                return render_template(
                    "profile_user.html",
                    history_buy_data = history_buy_data,
                    history_buy_pagination = history_buy_pagination,
                    user_data = user_data[0],
                    user = session['user']
                )
    else:
        return redirect(url_for('home'))

@app.route("/sell_history" , methods=["GET", "POST"])
def sell_history():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "select seller_ID , seller_Firstname , seller_Lastname , seller_Email , seller_Telephone , seller_Address , seller_Line , seller_Facebook , seller_Storename , seller_pic from seller where seller_ID = ?"
                val = [session['user']]
                print(val)
                cur.execute(sql,val)
                seller_data = cur.fetchall()
                shop_name = seller_data[0][8]
                print(shop_name)
                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )
                sql = "SELECT * FROM history where shop = ? and status is not ? "
                val = [shop_name,'in-cart']
                cur.execute(sql,val)
                total_data = cur.fetchall()
                print(len(total_data))
                sql = "SELECT * FROM history where shop = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [shop_name,'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_sell_data = cur.fetchall()
                history_sell_pagination= Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(total_data),
                    css_framework='bootstrap4'
                )
                
                for i in range(len(history_sell_data)):
                    history_sell_data[i] = list(history_sell_data[i])
                    history_sell_data[i][3] = str('{:,.2f}'.format(history_sell_data[i][3]*history_sell_data[i][5]))
                    if history_sell_data[i][8] == 'waiting':
                        history_sell_data[i][8] = str('รอการชำระเงิน')
                    if history_sell_data[i][8] == 'waiting_for_approve':
                        history_sell_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_sell_data[i][8] == 'cancel':
                        history_sell_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_sell_data[i][8] == 'confirm':
                        history_sell_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_sell_data[i] = tuple(history_sell_data[i])
                
                return render_template(
                    "sell_history_seller.html",
                    history_sell_pagination = history_sell_pagination,
                    history_sell_data = history_sell_data,
                    seller = session['user']
                )
    else:
        return redirect(url_for('home'))

@app.route("/buy_history" , methods=["GET", "POST"])
def buy_history():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                cur = connect.cursor()
                sql = "select seller_ID , seller_Firstname , seller_Lastname , seller_Email , seller_Telephone , seller_Address , seller_Line , seller_Facebook , seller_Storename , seller_pic from seller where seller_ID = ?"
                val = [session['user']]
                cur.execute(sql,val)
                seller_data = cur.fetchall()

                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )

                sql = "SELECT * FROM history where username = ? and status is not ?"
                val = [session['user'],'in-cart']
                cur.execute(sql,val)
                total_data = cur.fetchall()
                print(len(total_data))

                sql = "SELECT * FROM history where username = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [session['user'],'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_buy_data = cur.fetchall()
                history_buy_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(total_data),
                    css_framework='bootstrap4'
                )

                for i in range(len(history_buy_data)):
                    history_buy_data[i] = list(history_buy_data[i])
                    history_buy_data[i][3] = str('{:,.2f}'.format(history_buy_data[i][3]*history_buy_data[i][5]))
                    if history_buy_data[i][8] == 'waiting':
                        history_buy_data[i][8] = str('รอการชำระเงิน')
                    if history_buy_data[i][8] == 'waiting_for_approve':
                        history_buy_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'cancel':
                        history_buy_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'confirm':
                        history_buy_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_buy_data[i] = tuple(history_buy_data[i])
                
                return render_template(
                    "buy_history_seller.html",
                    seller_data = seller_data[0],
                    history_buy_pagination = history_buy_pagination,
                    history_buy_data = history_buy_data,
                    seller = session['user']
                )

        if session.get("role") == 'user':
            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                sql = "select user_ID , user_Firstname , user_Lastname , user_Email , user_Telephone , user_Address , user_pic from user where user_ID = ?"
                val = [session['user']]
                cur.execute(sql,val)
                user_data = cur.fetchall()
                page, per_page, offset = get_page_args(
                    page_parameter='page', 
                    per_page_parameter='per_page'
                )
                sql = "SELECT * FROM history where username = ? and status is not ?"
                val = [session['user'],'in-cart']
                cur.execute(sql,val)
                total_data = cur.fetchall()
                print(session['user'])
                sql = "SELECT * FROM history where username = ? and status is not ? ORDER BY date LIMIT ? OFFSET ?"
                val = [session['user'],'in-cart',per_page, offset]
                cur.execute(sql,val)
                history_buy_data = cur.fetchall()
                history_buy_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=len(total_data),
                    css_framework='bootstrap4'
                )


                for i in range(len(history_buy_data)):
                    history_buy_data[i] = list(history_buy_data[i])
                    history_buy_data[i][3] = str('{:,.2f}'.format(history_buy_data[i][3]*history_buy_data[i][5]))
                    if history_buy_data[i][8] == 'waiting':
                        history_buy_data[i][8] = str('รอการชำระเงิน')
                    if history_buy_data[i][8] == 'waiting_for_approve':
                        history_buy_data[i][8] = str('รอการอณุมัติคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'cancel':
                        history_buy_data[i][8] = str('ยกเลิกคำสั่งซื้อ')
                    if history_buy_data[i][8] == 'confirm':
                        history_buy_data[i][8] = str('อณุมัติคำสั่งซื้อ')
                    history_buy_data[i] = tuple(history_buy_data[i])

                return render_template(
                    "buy_history_user.html",
                    history_buy_data = history_buy_data,
                    history_buy_pagination = history_buy_pagination,
                    user_data = user_data[0],
                    user = session['user']
                )
    else:
        return redirect(url_for('home'))

@app.route("/ownerproduct_fish" , methods=["GET", "POST"])
def ownerproduct_fish():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                SellerID = session['user']
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute('select count(*) from fish_product where fish_Owner = ?',[SellerID])
                fish_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM fish_product where fish_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                fishproduct_data = cur.fetchall() 
                fish_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=fish_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(fishproduct_data)):
                    fishproduct_data[i] = list(fishproduct_data[i])
                    fishproduct_data[i][3] = str('{:,.2f}'.format(fishproduct_data[i][3]))
                    fishproduct_data[i][4] = str('{:,}'.format(int(fishproduct_data[i][4])))
                    fishproduct_data[i] = tuple(fishproduct_data[i])

                return render_template(
                    "ownerproduct_fish.html",
                    fish_pagination=fish_pagination,
                    seller_shop=seller[0], 
                    fishproduct_data=fishproduct_data, 
                    seller = session['user']
                )
    else:
        return redirect(url_for("home"))

@app.route("/ownerproduct_accessories" , methods=["GET", "POST"])
def ownerproduct_accessories():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                SellerID = session['user']
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from accessories_product where accessories_Owner = ?",[SellerID])
                accessories_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM accessories_product where accessories_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                accessoriesproduct_data = cur.fetchall() 
                accessories_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=accessories_total,
                    css_framework='bootstrap4'
                )
                for i in range(len(accessoriesproduct_data)):
                    accessoriesproduct_data[i] = list(accessoriesproduct_data[i])
                    accessoriesproduct_data[i][2] = str('{:,.2f}'.format(accessoriesproduct_data[i][2]))
                    accessoriesproduct_data[i][3] = str('{:,}'.format(int(accessoriesproduct_data[i][3])))
                    accessoriesproduct_data[i] = tuple(accessoriesproduct_data[i])

                return render_template(
                    "ownerproduct_accessories.html",
                    accessories_pagination=accessories_pagination,
                    seller_shop=seller[0], 
                    accessoriesproduct_data=accessoriesproduct_data, 
                    seller = session['user']
                )    
    else:
        return redirect(url_for("home"))
        
@app.route("/ownerproduct_tool" , methods=["GET", "POST"])
def ownerproduct_tool():
    if session.get("user",None) is not None:
        if session.get("role") == 'seller':
            with sqlite3.connect("mydata.db") as connect:
                SellerID = session['user']
                cur = connect.cursor()
                cur.execute("select * from seller where seller_id = ?",[SellerID])
                seller = cur.fetchall()

                cur.execute("select count(*) from tool_product where tool_Owner = ?",[SellerID])
                tool_total = cur.fetchone()[0]
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                sql = "SELECT * FROM tool_product where tool_Owner = ? ORDER BY time desc LIMIT ? OFFSET ?"
                val = [SellerID,per_page, offset]
                cur.execute(sql,val)
                toolproduct_data = cur.fetchall() 
                tool_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=tool_total,
                    css_framework='bootstrap4'
                )
                
                for i in range(len(toolproduct_data)):
                    toolproduct_data[i] = list(toolproduct_data[i])
                    toolproduct_data[i][2] = str('{:,.2f}'.format(toolproduct_data[i][2]))
                    toolproduct_data[i][3] = str('{:,}'.format(int(toolproduct_data[i][3])))
                    toolproduct_data[i] = tuple(toolproduct_data[i])

                return render_template(
                    "ownerproduct_tool.html",
                    tool_pagination=tool_pagination,
                    seller_shop=seller[0], 
                    toolproduct_data=toolproduct_data,
                    seller = session['user']
                )   
    else:
        return redirect(url_for("home"))
        
@app.route("/showData")
def showData():
    result = getPrediction()
    predict_result = np.argmax(result)
    accuracy = result[np.argmax(result)]*100
    if accuracy > 50 and accuracy < 100:
        if session.get("user",None) is not None:
            if session.get("role") == 'seller':
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    pos = int(predict_result)+1
                    cur.execute("select * from common_name where id = ?",[pos])
                    common_name = cur.fetchall()[0]
                    cur.execute("select * from fish_data where Common_name = ?",[common_name[1]])
                    # cur.execute("select * from fish_data where Name LIKE ?",["%"+common_name[1]+"%"])
                    fish_data = cur.fetchall()
                    fish_product_total = 0
                    for i in range(len(fish_data)):
                        cur.execute("select * from fish_product where fish_Name LIKE ?",["%"+fish_data[i][1]+"%"])
                        fish_product_data = cur.fetchall()
                        count = len(fish_product_data)
                        fish_product_total += count

                    fish_product_total = len(fish_product_data)
                    page, per_page, offset = get_page_args(page_parameter='page')
                    per_page = 12
                    if offset != 0:
                        offset = offset + 2
                    fish_product_list = []
                    for i in range(len(fish_data)):
                        sql = "SELECT * FROM fish_product where fish_Name LIKE ? ORDER BY fish_ID LIMIT ? OFFSET ?"
                        val = ["%"+fish_data[i][1]+"%",per_page, offset]
                        cur.execute(sql,val)
                        fish_product_data = cur.fetchall()
                        for i in range(len(fish_product_data)):
                            fish_product_list.append(fish_product_data[i])
                    
                    fish_pagination = Pagination(
                        page=page,
                        per_page=per_page,
                        total=fish_product_total,
                        css_framework='bootstrap4'
                    )
                    
                    sql = "SELECT fish_data.* , common_name.pic_fish from common_name INNER JOIN fish_data on common_name.name = fish_data.common_name where Common_Name = ? order by Common_Name"
                    val = [common_name[1]]
                    cur.execute(sql, val)
                    search_fish_data = cur.fetchall()
                    print(search_fish_data)

                    for i in range(len(fish_product_list)):
                        fish_product_list[i] = list(fish_product_list[i])
                        fish_product_list[i][3] = str('{:,.2f}'.format(fish_product_list[i][3]))
                        fish_product_list[i][4] = str('{:,}'.format(int(fish_product_list[i][4])))
                        fish_product_list[i] = tuple(fish_product_list[i])
                    if len(fish_product_list) == 0:
                        return render_template(
                            "no_one_sell_seller.html",
                            seller = session['user'],
                            search_fish_data = search_fish_data
                        )
                    else:
                        return render_template(
                            "result_seller.html", 
                            search_fish_data = search_fish_data,
                            predict_result = fish_data,
                            fish_product_list = fish_product_list,
                            fish_pagination = fish_pagination,
                            seller = session['user']
                        )

            if session.get("role") == 'user':
                #loadimage, resize, to array
                with sqlite3.connect("mydata.db") as connect:
                    cur = connect.cursor()
                    pos = int(predict_result)+1
                    cur.execute("select * from common_name where id = ?",[pos])
                    common_name = cur.fetchall()[0]
                    cur.execute("select * from fish_data where Common_name = ?",[common_name[1]])
                    # cur.execute("select * from fish_data where Name LIKE ?",["%"+common_name[1]+"%"])
                    fish_data = cur.fetchall()
                    fish_product_total = 0
                    for i in range(len(fish_data)):
                        cur.execute("select * from fish_product where fish_Name LIKE ?",["%"+fish_data[i][1]+"%"])
                        fish_product_data = cur.fetchall()
                        count = len(fish_product_data)
                        fish_product_total += count

                    fish_product_total = len(fish_product_data)
                    page, per_page, offset = get_page_args(page_parameter='page')
                    per_page = 12
                    if offset != 0:
                        offset = offset + 2
                    fish_product_list = []
                    for i in range(len(fish_data)):
                        sql = "SELECT * FROM fish_product where fish_Name LIKE ? ORDER BY fish_ID LIMIT ? OFFSET ?"
                        val = ["%"+fish_data[i][1]+"%",per_page, offset]
                        cur.execute(sql,val)
                        fish_product_data = cur.fetchall()
                        for i in range(len(fish_product_data)):
                            fish_product_list.append(fish_product_data[i])
                    
                    fish_pagination = Pagination(
                        page=page,
                        per_page=per_page,
                        total=fish_product_total,
                        css_framework='bootstrap4'
                    )

                    for i in range(len(fish_product_list)):
                        fish_product_list[i] = list(fish_product_list[i])
                        fish_product_list[i][3] = str('{:,.2f}'.format(fish_product_list[i][3]))
                        fish_product_list[i][4] = str('{:,}'.format(int(fish_product_list[i][4])))
                        fish_product_list[i] = tuple(fish_product_list[i])

                    sql = "SELECT fish_data.* , common_name.pic_fish from common_name INNER JOIN fish_data on common_name.name = fish_data.common_name where Common_Name = ? order by Common_Name"
                    val = [common_name[1]]
                    cur.execute(sql, val)
                    search_fish_data = cur.fetchall()
                    print(search_fish_data)

                    if len(fish_product_list) == 0:
                        return render_template(
                            "no_one_sell_user.html",
                            user = session['user'],
                            search_fish_data = search_fish_data
                        )
                    else:
                        return render_template(
                            "result_user.html", 
                            search_fish_data = search_fish_data,
                            predict_result = fish_data,
                            fish_product_list = fish_product_list,
                            fish_pagination = fish_pagination,
                            user = session['user']
                        )

        else:

            with sqlite3.connect("mydata.db") as connect:
                cur = connect.cursor()
                pos = int(predict_result)+1
                cur.execute("select * from common_name where id = ?",[pos])
                common_name = cur.fetchall()[0]
                cur.execute("select * from fish_data where Common_name = ?",[common_name[1]])
                # cur.execute("select * from fish_data where Name LIKE ?",["%"+common_name[1]+"%"])
                fish_data = cur.fetchall()
                fish_product_total = 0
                for i in range(len(fish_data)):
                    cur.execute("select * from fish_product where fish_Name LIKE ?",["%"+fish_data[i][1]+"%"])
                    fish_product_data = cur.fetchall()
                    count = len(fish_product_data)
                    fish_product_total += count

                fish_product_total = len(fish_product_data)
                page, per_page, offset = get_page_args(page_parameter='page')
                per_page = 12
                if offset != 0:
                    offset = offset + 2
                fish_product_list = []
                for i in range(len(fish_data)):
                    sql = "SELECT * FROM fish_product where fish_Name LIKE ? ORDER BY fish_ID LIMIT ? OFFSET ?"
                    val = ["%"+fish_data[i][1]+"%",per_page, offset]
                    cur.execute(sql,val)
                    fish_product_data = cur.fetchall()
                    for i in range(len(fish_product_data)):
                        fish_product_list.append(fish_product_data[i])
                
                fish_pagination = Pagination(
                    page=page,
                    per_page=per_page,
                    total=fish_product_total,
                    css_framework='bootstrap4'
                )

                for i in range(len(fish_product_list)):
                    fish_product_list[i] = list(fish_product_list[i])
                    fish_product_list[i][3] = str('{:,.2f}'.format(fish_product_list[i][3]))
                    fish_product_list[i][4] = str('{:,}'.format(int(fish_product_list[i][4])))
                    fish_product_list[i] = tuple(fish_product_list[i])

                sql = "SELECT fish_data.* , common_name.pic_fish from common_name INNER JOIN fish_data on common_name.name = fish_data.common_name where Common_Name = ? order by Common_Name"
                val = [common_name[1]]
                cur.execute(sql, val)
                search_fish_data = cur.fetchall()
                print(search_fish_data)

                if len(fish_product_list) == 0:
                    return render_template(
                        "no_one_sell.html",
                        search_fish_data = search_fish_data
                    )
                else:
                    return render_template(
                        "result.html", 
                        predict_result = fish_data,
                        fish_product_list = fish_product_list,
                        fish_pagination = fish_pagination,
                        search_fish_data = search_fish_data
                    )

    else:
        if session.get("user",None) is not None:
            if session.get("role") == 'seller':
                return render_template(
                    "result_cannot_search_seller.html",
                    seller = session['user']
                )
            if session.get("role") == 'user':
                return render_template(
                    "result_cannot_search_user.html",
                    user = session['user']
                )
        else:
            return render_template(
                "result_cannot_search.html"
            )
            
########################################################
if __name__ == "__main__":
    app.secret_key = "fish1234567803102541fish"
    app.run(port=8000,debug=True)
