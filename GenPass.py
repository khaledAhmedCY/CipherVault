from flask import Flask, render_template, request, jsonify
import random
import string

from check import check_strenght 

app = Flask(__name__)

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

# 2. إضافة Route لفتح صفحة فحص القوة (StrengthP.html)
@app.route('/strength')
def strength_page(): 
    return render_template('strength.html')

@app.route('/login')
def login():  
    return render_template('LoginP.html')


@app.route('/signup')
def signup():  
    return render_template('SignUpP.html')

# 3. إضافة Route لاستقبال كلمة المرور وفحصها باستخدام ملف check.py
@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data.get('password', '')
    
    # مناداة الدالة اللي جاية من ملف check.py
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