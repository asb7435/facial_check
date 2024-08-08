from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import log_attendance, add_user, get_users, delete_user, load_known_faces, update_user, get_user_info, get_user_logs, get_today_logs, check_existing_name, check_existing_face
from face_recognition import get_face_encodings, compare_faces
import cv2
import numpy as np
import base64
import re
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

known_faces = load_known_faces()
user_check_in_status = {}  # 사용자 출근 상태를 저장하는 메모리 변수

def generate_user_id():
    return 'a' + ''.join(random.choices('0123456789', k=7))

@app.route('/')
def index():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    return render_template('index.html', title="Home")

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    data = request.get_json()
    image_data = data['image']
    status = data['status']  # 'check_in' or 'check_out'
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    np_img = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    encodings = get_face_encodings(img)

    for encoding in encodings:
        for user_id, known_encodings in known_faces.items():
            if any(compare_faces(np.array(known_encodings), encoding)):
                if status == 'check_in':
                    if user_id not in user_check_in_status:
                        user_check_in_status[user_id] = True
                        log_attendance(user_id, 'check_in')
                        return jsonify({"status": "success", "message": f"User {user_id} checked in successfully."})
                    else:
                        return jsonify({"status": "error", "message": "Already checked in."})
                
                elif status == 'check_out':
                    if user_id in user_check_in_status:
                        del user_check_in_status[user_id]
                        log_attendance(user_id, 'check_out')
                        return jsonify({"status": "success", "message": f"User {user_id} checked out successfully."})
                    else:
                        return jsonify({"status": "error", "message": "Not checked in yet."})
                    
    return jsonify({"status": "error", "message": "Face not recognized."})

@app.route('/admin')
def admin():
    return render_template('admin_login.html', title="Admin Login")

@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'admin':
        session['admin_logged_in'] = True
        return redirect(url_for('index'))
    else:
        return "Invalid credentials"

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))

@app.route('/members')
def members():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    return render_template('members.html', title="Members")

@app.route('/members_list')
def members_list():
    members_list = get_users()
    return jsonify({"members": members_list})

@app.route('/member/<user_id>')
def member(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    member_info = get_user_info(user_id)
    if member_info:
        member_info['image'] = "data:image/png;base64," + member_info['image']
    return render_template('member.html', title=f"Member: {member_info['name']}", member=member_info)

@app.route('/member_logs/<user_id>')
def member_logs(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    logs = get_user_logs(user_id)
    return render_template('member_logs.html', title=f"Logs for User {user_id}", logs=logs, user_id=user_id)

@app.route('/logs/<user_id>')
def logs(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    logs = get_user_logs(user_id)
    return jsonify({"logs": logs})

@app.route('/today_logs')
def today_logs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    logs = get_today_logs()
    return render_template('today_logs.html', title="Today's Attendance", logs=logs)

@app.route('/register_member')
def register_member():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    return render_template('register.html', title="Register Member")

@app.route('/edit_member/<user_id>')
def edit_member(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    member_info = get_user_info(user_id)
    return render_template('edit_member.html', title=f"Edit Member: {member_info['name']}", member=member_info)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    phone = data['phone']
    gender = data['gender']
    memo = data['memo']
    user_id = generate_user_id()
    image_data = data['image']
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    np_img = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    encodings = get_face_encodings(img)

    if check_existing_face(encodings):
        return jsonify({"status": "error", "message": "Face already registered."})

    if len(encodings) > 0:
        name_count = check_existing_name(name)
        if name_count > 0:
            name += '*' * name_count

        if user_id not in known_faces:
            known_faces[user_id] = []
        known_faces[user_id].extend(encodings)
        add_user(user_id, name, phone, gender, memo, known_faces[user_id])
        return jsonify({"status": "success", "message": f"{name} registered successfully.", "user_id": user_id})
    else:
        return jsonify({"status": "error", "message": "No face detected."})

@app.route('/update_member', methods=['POST'])
def update_member():
    data = request.get_json()
    user_id = data['user_id']
    phone = data['phone']
    gender = data['gender']
    memo = data['memo']
    image_data = data['image']
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    np_img = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    encodings = get_face_encodings(img)

    if len(encodings) > 0:
        known_faces[user_id] = encodings
        update_user(user_id, phone, gender, memo, known_faces[user_id])
        return jsonify({"status": "success", "message": f"User {user_id} updated successfully."})
    else:
        return jsonify({"status": "error", "message": "No face detected."})

@app.route('/delete_member', methods=['POST'])
def delete_member():
    data = request.get_json()
    user_id = data['user_id']
    delete_user(user_id)
    if user_id in known_faces:
        del known_faces[user_id]
    return jsonify({"status": "success", "message": f"User {user_id} deleted successfully."})

if __name__ == '__main__':
    app.run(debug=True)
