from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random
import string
import os
from flask_sqlalchemy import SQLAlchemy
from ManagePass import init_manager_routes 
from check import check_strenght 

app = Flask(__name__)
app.secret_key = 'cipher_vault_encryption_key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

init_manager_routes(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# منطق توليد كلمة المرور
def generate_pass(length, use_upper, use_lower, use_digits, use_symbols):
    if length < 8:
        return "Length should be at least 8"
    uppercases = string.ascii_uppercase
    lowercases = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*_-=+/"
    all_chars = ""
    password = []
    if use_upper:
        all_chars += uppercases
        password.append(random.choice(uppercases))
    if use_lower:
        all_chars += lowercases
        password.append(random.choice(lowercases))
    if use_digits:
        all_chars += digits
        password.append(random.choice(digits))
    if use_symbols:
        all_chars += symbols
        password.append(random.choice(symbols))
    if all_chars == "":
        return "You must select at least one character type"
    for _ in range(length - len(password)):
        password.append(random.choice(all_chars))
    random.shuffle(password)
    return ''.join(password)


@app.route('/')
def index():
    return render_template('MainP.html')

@app.route('/generator')
def generator_page():
    return render_template('Generator.html')

@app.route('/strength')
def strength_page(): 
    return render_template('strength.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_name'] = user.username 
            return redirect(url_for('index'))
        else:
            return "Error: Invalid Email or Password"
    return render_template('LoginP.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form.get('username')
        user_email = request.form.get('email')
        user_pass = request.form.get('password')
        new_user = User(username=user_name, email=user_email, password=user_pass)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('SignUpP.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('index'))

@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data.get('password', '')
    result = check_strenght(password) 
    return jsonify({"strength": result})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    length = int(data.get('length', 8))
    use_upper = data.get('upper', True)
    use_lower = data.get('lower', True)
    use_digits = data.get('digits', True)   
    use_symbols = data.get('symbols', True)
    new_password = generate_pass(length, use_upper, use_lower, use_digits, use_symbols)
    return jsonify({"password": new_password})

if __name__ == '__main__':
    app.run(debug=True)