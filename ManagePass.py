from flask import request, jsonify, session, render_template, redirect, url_for
from cryptography.fernet import Fernet
from datetime import datetime

# --- 1. إعدادات التشفير (التي كانت في كود البايثون الخاص بك) ---
# ملحوظة: تأكد أن المفتاح صحيح وطوله مناسب لـ Fernet
key = b'kIbeBFx8JFBR5RrPc-kcv-QkhwE_xlsdVDfjsdc279o=' 
cipher = Fernet(key)

def encryption(password_text):
    password_bytes = password_text.encode() 
    encrypted_data = cipher.encrypt(password_bytes)
    return encrypted_data.decode()

def decryption(encrypted_text):
    encrypted_bytes = encrypted_text.encode()
    decrypted_data = cipher.decrypt(encrypted_bytes)
    return decrypted_data.decode()



# --- 2. دمج العمليات داخل مسارات الفلاسك ---

def init_manager_routes(app, db):
    
    class PasswordEntry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        platform = db.Column(db.String(100), nullable=False)
        saved_password = db.Column(db.String(500), nullable=False)
        strength = db.Column(db.String(50))
        user_name = db.Column(db.String(100))
        date_saved = db.Column(db.DateTime, default=datetime.utcnow)

    @app.route('/manager')
    def manager_page():
        if 'user_name' not in session:
            return redirect(url_for('login'))
        return render_template('ManagePass.html')

    @app.route('/save_password', methods=['POST'])
    def save_password():
        if 'user_name' not in session:
            return jsonify({"error": "Login required!"}), 401
        
        data = request.get_json()
        raw_password = data.get('password')

        # استخدام فنكشن التشفير هنا قبل الحفظ في الداتا بيز
        encrypted_pass = encryption(raw_password)

        new_entry = PasswordEntry(
            platform=data.get('platform'),
            saved_password=encrypted_pass, # بنخزن المشفر
            strength=data.get('strength'),
            user_name=session['user_name'],
            date_saved=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Saved & Encrypted!"})

    @app.route('/get_passwords')
    def get_passwords():
        if 'user_name' not in session:
            return jsonify([])
        
        entries = PasswordEntry.query.filter_by(user_name=session['user_name']).all()
        results = []
        
        for e in entries:
            try:
                real_password = decryption(e.saved_password)
            except Exception as err:
                real_password = "Error: Key Mismatch"

            results.append({
                "platform": e.platform,
                "password": real_password,
                "strength": e.strength,
                "date_saved": e.date_saved.strftime("%Y-%m-%d") # أضفنا التاريخ هنا
            })
        return jsonify(results)