#!/Users/panzichen/anaconda3/bin python3.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, abort, flash, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


DB_USER = "zp2197"
DB_PASSWORD = "rGXsjkDZZD"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
    if 'name' in session:
        print(session['name'])
        session.pop('user_id', None)
        session.pop('name', None)
        session.pop('password', None)
        session.pop('category', None)
    return redirect(url_for('login_page'))
    
    '''
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  print (request.args)
  
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  context = dict(data = names)

  return render_template("index.html", **context)
  '''


'''
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print (name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')
'''

# Signup Code

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')

@app.route('/signup', methods=['POST'])
def signup():
    input_name = str(request.form['name'])
    input_gender = str(request.form['gender'])
    input_password = str(request.form['password'])
    input_category = str(request.form['category'])
    input_address = str(request.form['address'])
    
    cmd = 'SELECT * FROM users WHERE users.name = (:inputname)'
    cursor = g.conn.execute(text(cmd), inputname = input_name)
    record = cursor.fetchone()
    cursor.close()
    
    # name already exists
    if record:
        context = dict(data = 'Name already exists!')
        return render_template("signup.html", **context)
    # name is ok
    else:
        # generate user_id
        cursor = g.conn.execute("SELECT MAX(user_id) FROM users")
        temp = cursor.fetchone()[0]
        if temp:
            user_id = int(temp) + 1
            print(user_id) # for debug
        else:
            user_id = 1
        cursor.close()
        
        # insert into table users and customers / sellers
        try:
            cmd = 'INSERT INTO users(user_id, name, gender, password) VALUES (:uid, :nm, :gd, :pw)'
            g.conn.execute(text(cmd), uid = user_id, nm = input_name, gd = input_gender, pw = input_password)
            if input_category == 'customer':
                cmd = 'INSERT INTO customers(user_id, address) VALUES (:uid, :ad)'
                g.conn.execute(text(cmd), uid = user_id, ad = input_address)
            elif input_category == 'seller':
                cmd = 'INSERT INTO sellers(user_id, address) VALUES (:uid, :ad)'
                g.conn.execute(text(cmd), uid = user_id, ad = input_address)
        except Exception as e:
            print (e)
            context = dict(data = 'uh oh, problem inserting into database')
            return render_template("signup.html", **context)
        
        
        return redirect(url_for('signup_success'))

# Signup Code End
        
# Login Code

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    input_name = str(request.form['name'])
    input_password = str(request.form['password'])
    
    cmd = 'SELECT * FROM users WHERE users.name = (:username)'
    cursor = g.conn.execute(text(cmd), username = input_name)
    record = cursor.fetchone()
    cursor.close()
    
    # if name exists
    if record:
        db_password = record['password']
        db_userid = record['user_id']
        
        # search for category
        cmd = 'SELECT * FROM customers WHERE customers.user_id = (:userid)'
        cursor = g.conn.execute(text(cmd), userid = db_userid)
        category_if = cursor.fetchone()
        cursor.close()
        
        if category_if:
            db_category = 'customer'
        else:
            db_category = 'seller'
    
    # if name does not exist
    else:
        context = dict(data = 'No username! Please sign up!')
        return render_template("login.html", **context)
    
    # if passsword is correct
    if input_password == db_password:
        session['user_id'] = db_userid
        session['name'] = input_name
        session['password'] = input_password
        session['category'] = db_category
        if db_category == 'seller':
            return redirect(url_for('seller_main'))
        else:
            return redirect(url_for('customer_main'))
    # if password is wrong
    else:
        context = dict(data = 'Wrong password!')
        return render_template("login.html", **context)

# Login Code End
        
# Logout Code

@app.route('/logout', methods=['POST', 'GET'])
def logout():
   session.pop('user_id', None)
   session.pop('name', None)
   session.pop('password', None)
   session.pop('category', None)
   return redirect(url_for('login_page'))

# Logout Code End

# Customer Code
   
@app.route('/customer_main')
def customer_main():
    
    # search for orders belonging to the customer
    cmd = 'SELECT order_id FROM orders WHERE orders.customer_id = (:customerid) ORDER BY order_id'
    cursor = g.conn.execute(text(cmd), customerid = session['user_id'])
    data = cursor.fetchall()
    cursor.close()
    
    result = []
    for item in data:
        result.append(item['order_id'])
    
    context = dict(data = result)
        
    return render_template('customer_main.html', **context)
    

@app.route('/add_order', methods=['POST'])
def add_order():
    
    # generate order_id
    cursor = g.conn.execute("SELECT MAX(order_id) FROM orders")
    temp = cursor.fetchone()[0]
    if temp:
        order_id = int(temp) + 1
        print(order_id) # for debug
    else:
        order_id = 1
    cursor.close()
    
    # insert into orders
    try:
        cmd = 'INSERT INTO orders(order_id, customer_id) VALUES (:oid, :cid)'
        g.conn.execute(text(cmd), oid = order_id, cid = session['user_id'])
    except Exception as e:
        print (e)
    
    return redirect(url_for('customer_main'))

@app.route('/delete_order', methods=['POST', 'GET'])
def delete_order():
    order_id = int(request.args.get('order_id'))
    
    
    try:
        
        # add deleted product quantity to table products
        cmd = 'SELECT product_id, quantity \
                FROM orders_products \
                WHERE order_id = (:oid)'
        cursor = g.conn.execute(text(cmd), oid = order_id)
        data = cursor.fetchall()
        cursor.close()
        
        for item in data:
            cmd = 'UPDATE products \
                SET quantity = quantity + (:qt) \
                WHERE product_id = (:pid)'
            cursor = g.conn.execute(text(cmd), qt = item['quantity'], pid = item['product_id'])
        
        # delete records in orders_products
        cmd = 'DELETE FROM orders_products WHERE order_id = (:oid)'
        g.conn.execute(text(cmd), oid = order_id)
        
        # delete records in orders
        cmd = 'DELETE FROM orders WHERE order_id = (:oid)'
        g.conn.execute(text(cmd), oid = order_id)
    
    except Exception as e:
        print (e)
        string = 'Delete fail!'
        return render_template('customer_main.html', string=string)
    
    string = 'Delete success!'
    return render_template('customer_main.html', string=string)



@app.route('/order', methods=['POST', 'GET'])
def order():
    
    # search for products belonging to the order
    order_id = int(request.args.get('order_id'))
    print(order_id)
    cmd = 'SELECT products.product_id, name, price, orders_products.quantity \
           FROM orders_products, products \
           WHERE order_id = (:orderid) AND orders_products.product_id = products.product_id'
    cursor = g.conn.execute(text(cmd), orderid = order_id)
    data = cursor.fetchall()
    cursor.close()
    
    result = []
    # search and display coupon info by product
    for item in data:
        
        row = {}
            
        cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item['product_id']))
        coupon_info = cursor.fetchall()
        cursor.close()
            
        # calculate the overall discount
        if coupon_info:
            discount = 1
            for c in coupon_info:
                print(c[0])
                discount *= (1 - c[0])
            discount = round((1 - discount), 2)
        else:
            discount = 0
            
        row['product_id'] = item['product_id']
        row['name'] = item['name']
        row['price'] = item['price']
        row['quantity'] = item['quantity']
        row['discount'] = discount
        result.append(row)
        
        # debug
        print(row['discount'])
        
    #context = dict(data = result)
    # calculate total price
    total_price = 0
    for each in result:
        total_price += each['price'] * each['quantity'] * (1 - each['discount'])
    
    print(total_price)
        
    return render_template('order.html', data = result, order_id = order_id, total_price = total_price) 


@app.route('/add_product_page')
def add_product_page():
    order_id = request.args.get('order_id')
    return render_template('add_product.html', order_id = order_id)


@app.route('/order_page')
def order_page():
    return render_template('order.html')


@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    order_id = int(request.form['order_id'])
    product_id = str(request.form['product_id'])
    number_to_add = str(request.form['number_to_add'])
    
    # product_id not a number
    if not product_id.isdigit():
        string = 'Input error! prodcuct_id not a number!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    
    # number_to_add not a number
    if not number_to_add.isdigit():
        string = 'Input error! number_to_add not a number!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    product_id = int(product_id)
    number_to_add = int(number_to_add)
    print(product_id)
    print(number_to_add)
    
    
    # judge if the product_id exists in database; if no, error
    cmd = "SELECT * \
            FROM products \
            WHERE products.product_id = (:pid)"
    cursor = g.conn.execute(text(cmd), pid = product_id)
    data = cursor.fetchall()
    cursor.close()
    if not data: 
        string = 'Sorry! The product does not exist!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    # judge if the product exists in the order; if yes, deny add request
    cmd = "SELECT * \
            FROM orders_products \
            WHERE orders_products.order_id = (:oid) AND \
            orders_products.product_id = (:pid)"
    cursor = g.conn.execute(text(cmd), oid = order_id, pid = product_id)
    data = cursor.fetchall()
    cursor.close()
    if data: 
        string = 'Sorry! The product already exists in this order!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    # judge if the number_to_add exceed the quantity rest(quantity in table products)
    cmd = "SELECT quantity \
            FROM products \
            WHERE products.product_id = (:pid)"
    cursor = g.conn.execute(text(cmd), pid = product_id)
    quantity_left = cursor.fetchone()['quantity']
    cursor.close()
    
    if number_to_add > quantity_left: 
        string = 'Sorry! The product is out of stock!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    # add product
    try:
        # add product to corresponding order
        cmd = 'INSERT INTO orders_products(order_id, product_id, quantity) VALUES (:oid, :pid, :qt)'
        g.conn.execute(text(cmd), oid = order_id, pid = product_id, qt = number_to_add)
        
        # minus the quantity from stock
        cmd2 = 'UPDATE products SET quantity = (:qt) WHERE product_id = (:pid)'
        g.conn.execute(text(cmd2), pid = product_id, qt = quantity_left - number_to_add)
        
    except Exception as e:
        print (e)
        string = 'Add error!'
        return render_template('add_product.html', order_id = order_id, string=string)
    
    string = 'Add product success!'
    return render_template('add_product.html', order_id = order_id, string=string)

@app.route('/delete_product', methods=['POST', 'GET'])
def delete_product():
    
    order_id = int(request.args.get('order_id'))
    product_id = int(request.args.get('product_id'))
    delete_number = int(request.args.get('delete_number'))
    
    try:
        
        # update the quantity in table products
        cmd = 'UPDATE products \
                SET quantity = quantity + (:qt) \
                WHERE product_id = (:pid)'
        g.conn.execute(text(cmd), qt = delete_number, pid = product_id)
        
        # delete records in orders_products
        cmd = 'DELETE FROM orders_products WHERE order_id = (:oid) AND product_id = (:pid)'
        g.conn.execute(text(cmd), oid = order_id, pid = product_id)
        
    except Exception as e:
        print (e)
        string = 'Delete fail!'
        return render_template('order.html', order_id = order_id, string=string)
    
    string = 'Delete success!'
    return render_template('order.html', order_id = order_id, string=string)
    
    


@app.route('/update_product', methods=['POST', 'GET'])
def update_product():
    
    order_id = int(request.form['order_id'])
    product_id = str(request.form['product_id'])
    number_to_update = str(request.form['number_to_update'])
    
    # product_id not a number
    if not product_id.isdigit():
        string = 'Input error! prodcuct_id not a number!'
        return render_template('order.html', order_id = order_id, string=string)
    
    
    # number_to_add not a number
    if not number_to_update.isdigit():
        string = 'Input error! number_to_update not a number!'
        return render_template('order.html', order_id = order_id, string=string)
    
    product_id = int(product_id)
    number_to_update = int(number_to_update)
    print(product_id)
    print(number_to_update)
    
    # judge if the product exist in this order
    cmd = "SELECT * \
            FROM orders_products \
            WHERE orders_products.product_id = (:pid) AND \
            orders_products.order_id = (:oid)"
    cursor = g.conn.execute(text(cmd), pid = product_id, oid = order_id)
    data = cursor.fetchall()
    cursor.close()
    if not data: 
        string = 'Sorry! The product does not exist in this order!'
        return render_template('order.html', order_id = order_id, string=string)
    
    # judge if the update number exceeds
    cmd = "SELECT quantity \
            FROM products \
            WHERE products.product_id = (:pid)"
    cursor = g.conn.execute(text(cmd), pid = product_id)
    quantity_left = cursor.fetchone()['quantity']
    print('quantity_left', quantity_left)
    cursor.close()
    
    cmd = "SELECT quantity \
            FROM orders_products \
            WHERE orders_products.order_id = (:oid) AND \
                orders_products.product_id = (:pid)"
    cursor = g.conn.execute(text(cmd), oid = order_id, pid = product_id)
    quantity_now = cursor.fetchone()['quantity']
    print('quantity_now', quantity_now)
    cursor.close()
    
    if number_to_update > quantity_left + quantity_now:
        string = 'Sorry! The product is out of stock!'
        return render_template('order.html', order_id = order_id, string=string)
    
    # update quantity
    try:
        # update quantity in table products
        cmd = 'UPDATE orders_products \
                SET quantity = (:qt) \
                WHERE order_id = (:oid) and product_id = (:pid)'
        g.conn.execute(text(cmd), oid = order_id, pid = product_id, qt = number_to_update)
        
        # update quantity in table orders_products
        cmd2 = 'UPDATE products SET quantity = (:qt) WHERE product_id = (:pid)'
        g.conn.execute(text(cmd2), pid = product_id, qt = quantity_left + quantity_now - number_to_update)
        
    except Exception as e:
        print (e)
        string = 'Update error!'
        return render_template('order.html', order_id = order_id, string=string)
    
    string = 'Change quantity success!'
    return render_template('order.html', order_id = order_id, string=string)


@app.route('/search_product', methods=['POST', 'GET'])
def search_product():
    
    order_id = int(request.form['order_id'])
    # search by keyword
    if request.form['submit_button'] == 'search' and request.form['keyword']:
        keyword = str(request.form['keyword']) # let's say air
        keyword_upper = keyword.upper() # AIR
        keyword_lower = keyword.lower() # air
        keyword_first_upper = keyword.lower()[0].upper() + keyword.lower()[1:] # Air
        
        cursor = g.conn.execute("SELECT product_id, name, description, price, quantity \
                                FROM products \
                                WHERE quantity > 0 \
                                ORDER BY product_id")
        data = cursor.fetchall()
        cursor.close()
        
        result = []
        # search and display coupon info by product
        for item in data:
            
            if (keyword_upper not in item['name']) and (keyword_lower not in item['name']) \
            and (keyword_first_upper not in item['name']): continue
            
            row = {}
            
            cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item[0]))
            coupon_info = cursor.fetchall()
            cursor.close()
            
            # calculate the overall discount
            if coupon_info:
                discount = 1
                for c in coupon_info:
                    discount *= (1 - c[0])
                discount = round(1 - discount, 2)
            else:
                discount = 0
            
            row['product_id'] = item['product_id']
            row['name'] = item['name']
            row['description'] = item['description']
            row['price'] = item['price']
            row['quantity'] = item['quantity']
            row['discount'] = discount
            result.append(row)
        
        context = dict(data = result)
        
        return render_template('add_product.html', **context, order_id = order_id)
    
    # search all
    elif request.form['submit_button'] == 'search all' or (request.form['submit_button'] == 'search' and (not request.form['keyword'])):
        
        cursor = g.conn.execute("SELECT product_id, name, description, price, quantity \
                                FROM products \
                                WHERE quantity > 0 \
                                ORDER BY product_id")
        data = cursor.fetchall()
        cursor.close()
        
        result = []
        # search and display coupon info by product
        for item in data:
            
            row = {}
            
            cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item[0]))
            coupon_info = cursor.fetchall()
            cursor.close()
            
            # calculate the overall discount
            if coupon_info:
                discount = 1
                for c in coupon_info:
                    discount *= (1 - c[0])
                discount = round(1 - discount, 2)
            else:
                discount = 0
            
            row['product_id'] = item['product_id']
            row['name'] = item['name']
            row['description'] = item['description']
            row['price'] = item['price']
            row['quantity'] = item['quantity']
            row['discount'] = discount
            result.append(row)
        
        context = dict(data = result)
        
        return render_template('add_product.html', **context, order_id = order_id)



# Customer Code End

# Seller Code

@app.route('/seller_main', methods=['POST', 'GET'])
def seller_main():
    return render_template('seller_main.html')

@app.route('/add_success', methods=['POST', 'GET'])
def add_success():
    return render_template('add_success.html')

@app.route('/add_failure', methods=['POST', 'GET'])
def add_failure():
    return render_template('add_failure.html')

@app.route('/add_coupon_success', methods=['POST', 'GET'])
def add_coupon_success():
    return render_template('add_coupon_success.html')

@app.route('/delete_success', methods=['POST', 'GET'])
def delete_success():
    return render_template('delete_success.html')

@app.route('/delete_coupon_success', methods=['POST', 'GET'])
def delete_coupon_success():
    return render_template('delete_coupon_success.html')


@app.route('/delete_failure', methods=['POST', 'GET'])
def delete_failure():
    return render_template('delete_failure.html')


@app.route('/add_product_sell', methods=['POST', 'GET'])
def add_product_sell():
    return render_template('add_product_sell.html')

@app.route('/add_new_coupon_page', methods=['POST', 'GET'])
def add_new_coupon_page():
    
    cmd = 'SELECT product_id, name, description, price, quantity FROM products WHERE products.seller_id = (:serller_id)'
    cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
    data = cursor.fetchall()
    cursor.close()
    
    
    result = []
    for item in data:

        row = {}
        
        cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item['product_id']))
        coupon_info = cursor.fetchall()
        cursor.close()
            
        # calculate the overall discount
        if coupon_info:
            discount = 1
            for c in coupon_info:
                print(c[0])
                discount *= (1 - c[0])
            discount = round((1 - discount), 2)
        else:
            discount = 0
            
        row['product_id'] = item['product_id']
        row['name'] = item['name']
        row['description'] = item['description']
        row['price'] = item['price']
        row['quantity'] = item['quantity']
        row['discount'] = discount
        result.append(row)
        
    context = dict(data = result)
    
    return render_template('add_coupon.html',**context)



@app.route('/add_new_product', methods=['POST','GET'])
def add_new_product():
    input_product_name = str(request.form['product_name'])
    input_product_descrition = str(request.form['product_description'])
    input_product_price = str(request.form['product_price'])
    input_product_quantity = str(request.form['product_quantity'])
    
    # judge if name is blank
    if len(input_product_name) == 0:
        string = 'Invalid input name!'
        return render_template('add_failure.html', string = string)
        
    # judge if input price is reasonable
    try:
        # test if it is a number and if it is larger than 0 simultaneously
        if float(input_product_price) <= float(0):
            a = 1 / 0
    except Exception as e:
        string = 'Invalid input price!'
        return render_template('add_failure.html', string = string)
    
    input_product_price = float(input_product_price)
    
    # judge if quantity is valid
    if (not input_product_quantity.isdigit()) or int(input_product_quantity) <= 0:
        string = 'Invalid input quantity!'
        return render_template('add_failure.html', string = string)
    
    input_product_quantity = int(input_product_quantity)
    

    cursor = g.conn.execute("SELECT MAX(product_id) FROM products")
    temp = cursor.fetchone()[0]
    if temp:
        product_id = int(temp) + 1
        print(product_id) # for debug
    else:
        product_id = 1
    cursor.close()

    cmd = 'INSERT INTO products(product_id, name, description, price,seller_id,quantity) VALUES (:pd, :nm, :des, :pr, :sid,:quan)'
    g.conn.execute(text(cmd), pd = product_id, nm = input_product_name, des = input_product_descrition, pr = input_product_price, sid=session['user_id'],quan=input_product_quantity )

    return redirect(url_for('add_success'))




@app.route('/delete_product_page', methods=['POST', 'GET'])
def delete_product_page():

    cmd = 'SELECT product_id, name, description, price, quantity FROM products WHERE products.seller_id = (:serller_id)'
    cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
    data = cursor.fetchall()
    cursor.close()

    result = []
    for item in data:

        row = {}
        row['product_id'] = item['product_id']
        row['name'] = item['name']
        row['description'] = item['description']
        row['price'] = item['price']
        row['quantity'] = item['quantity']
        result.append(row)
    
    context = dict(data = result)
    
    print(session['user_id'])
    print(context)
    
    return render_template('delete_product.html',**context)



@app.route('/delete_seller_product', methods=['POST', 'GET'])
def delete_seller_product():
    
    product_id = int(request.args.get('product_id'))

    try:
        # delete from orders_products
        cmd = 'DELETE FROM orders_products \
                WHERE product_id = (:pid)'
        g.conn.execute(text(cmd), pid = product_id)
            
        # delete from coupon_applied
        cmd = 'DELETE FROM coupon_applied \
                WHERE product_id = (:pid)'
        g.conn.execute(text(cmd), pid = product_id)
            
        # delete from products
        cmd = 'DELETE FROM products \
                WHERE product_id = (:pid)'
        g.conn.execute(text(cmd), pid = product_id)
        
    except Exception as e:
        return redirect(url_for('delete_failure'))
        
    return redirect(url_for('delete_success'))


@app.route('/see_my_inventory', methods=['POST'])
def see_my_inventory():

    cmd = 'SELECT product_id, name, description, price, quantity FROM products WHERE products.seller_id = (:serller_id)'
    cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
    data = cursor.fetchall()
    cursor.close()
    
    
    result = []
    for item in data:

        row = {}
        
        cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item['product_id']))
        coupon_info = cursor.fetchall()
        cursor.close()
            
        # calculate the overall discount
        if coupon_info:
            discount = 1
            for c in coupon_info:
                print(c[0])
                discount *= (1 - c[0])
            discount = round((1 - discount), 2)
        else:
            discount = 0
            
        row['product_id'] = item['product_id']
        row['name'] = item['name']
        row['description'] = item['description']
        row['price'] = item['price']
        row['quantity'] = item['quantity']
        row['discount'] = discount
        result.append(row)
        
    context = dict(data = result)
    
    print(session['user_id'])
    print(context)
    
    return render_template('show_all_product.html',**context)



@app.route('/add_new_coupon', methods=['POST','GET'])
def add_new_coupon():
    discount_rate = str(request.form['discount_rate'])
    
    product_ids = str(request.form['product_ids'])
    
    # judge if discount_rate is reasonable
    try:
        # test if it is a number and if it is larger than 0 simultaneously
        if float(discount_rate) <= float(0) or float(discount_rate) >= float(1):
            a = 1 / 0
    except Exception as e:
        string = 'Invalid discount value!'
        return render_template('add_coupon_failure.html', string = string)
    
    # if apply the coupon to all
    if product_ids == 'all':
        
        # generate coupon_id
        cursor = g.conn.execute("SELECT MAX(coupon_id) FROM coupons")
        temp = cursor.fetchone()[0]
        if temp:
            coupon_id = int(temp) + 1
            print(coupon_id) # for debug
        else:
            coupon_id = 1
          
        cursor.close()
        
        # insert
        cmd = 'INSERT INTO coupons(coupon_id, discount, seller_id) VALUES (:cd, :dis, :sid)'
        g.conn.execute(text(cmd), cd = coupon_id, dis = discount_rate, sid=session['user_id'])
    
        cmd = 'SELECT product_id FROM products WHERE products.seller_id = (:serller_id)'
        cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
        data = cursor.fetchall()
        cursor.close()
    
    
        result = []
        for item in data:
            result.append(item['product_id'])
    
    
        for item in result:
    
            cmd = 'INSERT INTO coupon_applied(coupon_id, product_id) VALUES (:cd, :pid)'
            g.conn.execute(text(cmd), cd = coupon_id, pid = item)
    
        return redirect(url_for('add_coupon_success'))
    
    # if not apply to all
    else:
        # judge if product_ids are valid
        product_id_array = product_ids.strip().split(',')
        for pid in product_id_array:
            
            pid = str(pid.strip())
            
            # if id is not a number
            if not pid.isdigit():
                string = 'Invalid product_ids'
                return render_template('add_coupon_failure.html', string = string)
            
            pid = int(pid)
            
            # if product does not belong to the seller
            cmd = 'SELECT seller_id FROM products WHERE products.product_id = (:productid)'
            cursor = g.conn.execute(text(cmd), productid = pid)
            select = cursor.fetchone()
            cursor.close()
            if select['seller_id'] != session['user_id']:
                string = 'Add failure! You can only add coupons to your products!'
                return render_template('add_coupon_failure.html', string = string)
        
        # generate coupon_id
        cursor = g.conn.execute("SELECT MAX(coupon_id) FROM coupons")
        temp = cursor.fetchone()[0]
        if temp:
            coupon_id = int(temp) + 1
            print(coupon_id) # for debug
        else:
            coupon_id = 1
          
        cursor.close()
        
        # insert
        cmd = 'INSERT INTO coupons(coupon_id, discount, seller_id) VALUES (:cd, :dis, :sid)'
        g.conn.execute(text(cmd), cd = coupon_id, dis = discount_rate, sid=session['user_id'])
        
        for item in product_id_array:
    
            cmd = 'INSERT INTO coupon_applied(coupon_id, product_id) VALUES (:cd, :pid)'
            g.conn.execute(text(cmd), cd = coupon_id, pid = item)
    
        return redirect(url_for('add_coupon_success'))




@app.route('/delete_coupon', methods=['POST'])
def delete_coupon():

    cmd = 'SELECT coupon_id, discount FROM coupons WHERE coupons.seller_id = (:serller_id)'
    cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
    data = cursor.fetchall()
    cursor.close()

    result = []
    for item in data:

        row = {}
        row['coupon_id'] = item['coupon_id']
        row['discount'] = item['discount']
        result.append(row)
    
    context = dict(data = result)
    
    return render_template('delete_coupon.html',**context)




@app.route('/delete_coupon_seller', methods=['POST', 'GET'])
def delete_coupon_seller():
    
    coupon_id = int(request.args.get('coupon_id'))
   

    cmd = 'DELETE FROM coupon_applied\
               WHERE coupon_id = (:pid)'
    g.conn.execute(text(cmd), pid = coupon_id)


    cmd = 'DELETE FROM coupons\
               WHERE coupon_id = (:pid)'
    g.conn.execute(text(cmd), pid = coupon_id)
    
    return redirect(url_for('delete_coupon_success'))


@app.route('/delete_coupon_from_products_page', methods=['POST', 'GET'])
def delete_coupon_from_products_page():
    
    cmd = 'SELECT product_id, name, description, price, quantity FROM products WHERE products.seller_id = (:serller_id)'
    cursor = g.conn.execute(text(cmd), serller_id = session['user_id'])
    data = cursor.fetchall()
    cursor.close()
    
    
    result = []
    for item in data:

        row = {}
        
        cursor = g.conn.execute("SELECT coupons.discount \
                                    FROM coupon_applied, coupons \
                                    WHERE coupon_applied.product_id = '{}' and coupon_applied.coupon_id = coupons.coupon_id".format(item['product_id']))
        coupon_info = cursor.fetchall()
        cursor.close()
            
        # calculate the overall discount
        if coupon_info:
            discount = 1
            for c in coupon_info:
                discount *= (1 - c[0])
            discount = round((1 - discount), 2)
        else:
            discount = 0
            
        row['product_id'] = item['product_id']
        row['name'] = item['name']
        row['description'] = item['description']
        row['price'] = item['price']
        row['quantity'] = item['quantity']
        row['discount'] = discount
        result.append(row)
        
    context = dict(data = result)
    
    return render_template('delete_coupon_from_products.html',**context)



@app.route('/delete_coupon_from_products', methods=['POST', 'GET'])
def delete_coupon_from_products():
    product_id = int(request.args.get('product_id'))
    
    cmd = 'SELECT coupon_id FROM coupon_applied WHERE product_id = (:pid)'
    cursor = g.conn.execute(text(cmd), pid = product_id)
    cids = cursor.fetchall()
    cursor.close()
    
    cmd = 'DELETE FROM coupon_applied \
               WHERE product_id = (:pid)'
    g.conn.execute(text(cmd), pid = product_id)
    
    # delete cid from coupons if cid is not applied to any product
    for cid in cids:
        cmd = 'SELECT * FROM coupon_applied WHERE coupon_id = (:couponid)'
        cursor = g.conn.execute(text(cmd), couponid = cid['coupon_id'])
        flag = cursor.fetchall()
        cursor.close()
        
        if not flag:
             cmd = 'DELETE FROM coupons WHERE coupon_id = (:couponid)'
             g.conn.execute(text(cmd), couponid = cid['coupon_id'])     
    
    return redirect(url_for('delete_coupon_success'))
    

# Seller Code End


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
