from flask import Flask,request,jsonify,redirect,url_for,render_template,render_template_string
import sqlite3
import pickle
import base64

app = Flask(__name__)

def connect_database():
    return sqlite3.connect("penjualan.db")

@app.route('/')
def index():
  return render_template('index.html')

@app.route("/event")
def event():
  return render_template('event.html')

@app.route("/services")
def serive():
  return render_template('service.html')

@app.route("/menu")
def menu():
  return render_template('menu.html')

@app.route("/contact")
def contact():
  return render_template('contact.html')

@app.route("/product/<action>",methods=["POST","GET"])
def productAction(action):
    print(action,"=====")
    if request.method == "GET":
        if action == "add":
            return render_template("form.html")
        if action == "product_list":
            print("======")
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * from product")
            result = cursor.fetchall()

            data_product = {
                "id":[],
                "name":[],
                "category":[],
                "price":[],
                "thumbnail":[],
                "description":[],
            }

            for x in result:
                data_product["id"].append(x[0])
                data_product["name"].append(x[1])
                data_product["category"].append(x[2])
                data_product["price"].append(x[3])
                data_product["thumbnail"].append(base64.b64encode(x[5]).decode('utf-8'))
                data_product["description"].append(x[4])
            return jsonify(data_product)
        if action == "delete":
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("delete  from product where id = ?",(request.args["data"],))
            conn.commit()
            return jsonify({"status":"succes"})
        if action == "update":
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * from product where id = ?",(request.args.get("data"),))
            result = cursor.fetchone()
            return render_template("update.html",name=result[1],category=result[2],price=result[3],description=result[4],id=result[0])
        if str(action).isdigit():
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("select * from product where id = ?",(action,))
            result = cursor.fetchone()
            cursor.execute("select * from detail_product where id = ?",(action,))
            result2 = cursor.fetchone()
            image = pickle.loads(result2[2])
            imageList = []
            listImage = []
            if len(image) >1:
                imageList = image[1:]
                for data in imageList:
                    listImage.append(base64.b64encode(data).decode('utf-8'))
            return render_template("product-detail.html",description=result2[1],price=result[3],title=result[1],image=base64.b64encode(image[0]).decode('utf-8'),listImage=listImage)
    else:
        if action == "add":
            name = request.form["name"]
            price = request.form["price"]
            category = request.form["category"]
            description = request.form["description"]
            thumbnail = request.files.get("thumbnail")
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO product (name, price, category,description, thumbnail) VALUES (?, ?, ?, ?, ?)
            ''', (name, price, category,description, thumbnail.read()))
            conn.commit()
            return render_template("form.html",alert="<script>alert('data diinputkan')</script>")
        
        if action == "update":
            name = request.form["name"]
            price = request.form["price"]
            category = request.form["category"]
            description = request.form["description"]
            id = request.form["id"]
            print(name)
            print(price)
            print(category)
            print(description)
            con = connect_database()
            cursor = con.cursor()
            cursor.execute("""
            UPDATE product
            SET category = ?, price = ?, name= ?, description = ?
            WHERE id = ?
        """, (category, price, name,description,id))
            con.commit()

            return redirect(url_for("admin_dashboard"))


@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        connectDb = connect_database()
        cursor = connectDb.cursor()

        cursor.execute("SELECT * FROM admin where username =?",(username,))
        result = cursor.fetchone()
        print(result)
        if result != [] and result != None:
            if password ==  result[1]:
                return redirect(url_for("admin_dashboard"))
            return render_template("login.html")
    return render_template("login.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


if __name__ == '__main__':
  app.run(debug=True)