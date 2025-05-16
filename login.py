from flask import Flask, render_template, url_for, redirect
from flask import jsonify
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'secretkeyhi'

def load_user(user_id):
    return User.query.get(int(user_id))

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="bholupie",
        database="ecommerce"
    )
    return connection
class RegisterForm(FlaskForm):
    name= StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Name"})
    email = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "Email"})
    password= PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

    def validate_name(self, name):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE name = %s", (name.data,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
         raise ValidationError("THAT NAME ALREADY EXISTS")

class LoginForm(FlaskForm):
    name= StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Name"})
    email = StringField(validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "Email"})
    password= PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

def get_products_list():#get_products_list
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT p.id AS product_id, p.name AS product_name, p.price, p.image, c.id AS category_id, c.name AS category_name, b.id AS brand_id, b.name AS brand_name FROM products p INNER JOIN categories c ON p.category_id = c.id INNER JOIN brands b ON p.brand_id = b.id LIMIT 10;"


    cursor.execute(query)
    products = cursor.fetchall()# fetch all and store them in variable

    # cursor.close()
    # conn.close()

    return products
       

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        
        cursor.execute("SELECT * FROM users WHERE  email = %s", ( form.email.data,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            return render_template('dashboard.html', name=user['name'])  
        else:
            return render_template('login.html', form=form, error="Invalid email or password.")  
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
     return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (form.name.data,form.email.data, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Registered user:", form.name.data)

        return redirect(url_for('login'))
         

    return render_template('register.html', form=form)

# @app.route('/products')
# def get_products():
#     products = get_products_details()
#     return jsonify(products)

@app.route('/products', methods=['GET'])
def products():
    # my_array = ["apple", "banana", "cherry"]
    # return render_template('index.html', my_array=my_array)
    products = get_products_list()
    return render_template('product.html', product_list = products) 

@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    conn = get_db_connection()  
    cursor = conn.cursor(dictionary=True)  
    
    query = "SELECT p.id AS product_id, p.name AS product_name, p.price, p.image, c.id AS category_id, c.name AS category_name, b.id AS brand_id, b.name AS brand_name FROM products p INNER JOIN categories c ON p.category_id = c.id INNER JOIN brands b ON p.brand_id = b.id WHERE p.id = %s"
    cursor.execute(query,(id,))
    product = cursor.fetchone() 
    return render_template('product-detail.html', product=product)

if __name__ == '__main__':
    app.run(port=3000, debug=True)