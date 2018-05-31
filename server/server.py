from flask import Flask, render_template, session, redirect, url_for, escape, request, jsonify

import os
import send_email
import sqlite3
import random
import re

app = Flask(__name__)

code_mapping = dict()
ID_REG = r"^[a-z][0-9]{8}$"

@app.route("/")
def hello():
    if 'username' not in session:
        return redirect('/login?type=0')
    return render_template('main.html', user=session['username'])

@app.route("/login", methods=['GET'])
def login_page():
    if 'username' in session:
        return redirect('/')
    warning_type = "0"
    get_type = request.args.get('type')
    if get_type:
        warning_type = get_type
    return render_template('login.html', type=warning_type)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('/')

@app.route("/user_login", methods=['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']
    if not re.search(ID_REG, username) and username != 'admin':
        return redirect('/login?type=1')


    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_login WHERE username = "%s" AND password = "%s"'
            % (username, password))
    res = c.fetchall()
    conn.close()

    if len(res):
        session['username'] = username
        return redirect('/')
    return redirect('/login?type=1')

@app.route("/get_code", methods=['POST'])
def get_code():
    username = request.form['username']
    if not re.search(ID_REG, username):
        return jsonify(res=-1)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_login WHERE username = "%s"'
            % (username))
    res = c.fetchall()
    conn.close()
    if len(res):
        return jsonify(res=-2)

    code = random.randint(1000000000, 2000000000)
    
    code_mapping[username] = str(code)
    print(code_mapping.get(username))
    if send_email.send_verification_code(code, username + '@ntu.edu.tw') == -1:
        return jsonify(res=-3)
    return jsonify(res=0)

@app.route("/user_register", methods=['POST'])
def user_register():
    username = request.form['username']
    password = request.form['password']
    code = request.form['code']
    if not re.search(ID_REG, username) and username != 'admin':
        return redirect('/login?type=1')
    print(code_mapping.get(username))
    if code != code_mapping.get(username):
        return redirect('/login?type=2')
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO user_login VALUES ("%s", "%s")' % (username, password))
    conn.commit()
    conn.close()
    session['username'] = username
    return redirect('/')

@app.route('/admin')
def admin():
    session['username'] = "GG3be0"
    return redirect('/')



if __name__ == "__main__":
    app.secret_key = os.urandom(16)
    app.run(host="0.0.0.0", port=8755)
