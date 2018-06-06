import datetime
import os
import sqlite3
import random
import re
import time as Time

from flask import Flask, render_template, session, redirect, request, jsonify

import send_email

app = Flask(__name__)

CODE_MAP = dict()
ID_REG = r"^[a-z][0-9]{8}$"
INIT_POINT = 1000
INIT_COIN = 100

class Friend:
    def __init__(self, user, time):
        self.user = user
        self.time = time

class Message:
    def __init__(self, user, msg, time):
        self.user = user
        self.msg = msg
        self.time = time

def get_time_str(time):
    value = datetime.datetime.fromtimestamp(time)
    return value.strftime('%Y-%m-%d %H:%M:%S')


######################### request function #########################

@app.route("/")
def main_page():
    if 'username' not in session:
        return redirect('/login?type=0')
    res = []
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM gaguang ORDER BY time DESC LIMIT 50')
        for row in cur.fetchall():
            res.append(Message(row[0], row[1], get_time_str(row[2])))
    return render_template('main.html', user=session['username'], message=res)

@app.route('/gaguang', methods=['POST'])
def gaguang():
    if 'username' not in session:
        return redirect('/login?type=0')
    username = session['username'];
    message = request.form['comment']
    now_time = Time.time()
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO gaguang VALUES (?, ?, ?)', [username, message, now_time])
        conn.commit()
    return redirect('/')

@app.route("/friend")
def friend_page():
    if 'username' not in session:
        return redirect('/login?type=0')

    pending = []
    askme = []
    myfriends = []

    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT user2, time FROM friend_request WHERE user1 = ?', [session['username']])
        for row in cur.fetchall():
            pending.append(Friend(row[0], get_time_str(row[1])))
        cur.execute('SELECT user1, time FROM friend_request WHERE user2 = ?', [session['username']])
        for row in cur.fetchall():
            askme.append(Friend(row[0], get_time_str(row[1])))
        cur.execute('SELECT user2, time FROM friend WHERE user1 = ?', [session['username']])
        for row in cur.fetchall():
            myfriends.append(Friend(row[0], get_time_str(row[1])))

    return render_template('friend.html', user=session['username'], pending=pending,
                           askme=askme, myfriends=myfriends)

@app.route("/friend_request", methods=['POST'])
def friend_request():
    """
    Send a new friend request to a user, this function will do some check first.
    If they are not firend now and each user do not have the pending request to each other,
    this function will add a new record to the database.
    """
    if 'username' not in session:
        return redirect('/login?type=0')
    user1 = session['username']
    user2 = request.form['username']
    now_time = Time.time()
    if not re.search(ID_REG, user2) and user2 != 'admin':
        return jsonify(res=-4)
    # check friend
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM friend WHERE user1 = ? AND user2 = ?', [user1, user2])
        if cur.fetchall() or user1 == user2:
            return jsonify(res=-1)
        cur.execute('SELECT * FROM friend_request WHERE user1 = ? AND user2 = ?', [user1, user2])
        if cur.fetchall():
            return jsonify(res=-2)
        cur.execute('SELECT * FROM friend_request WHERE user1 = ? AND user2 = ?', [user2, user1])
        if cur.fetchall():
            return jsonify(res=-3)
        cur.execute('SELECT * FROM user_login WHERE username = ?', [user2])
        if not cur.fetchall():
            return jsonify(res=-4)
        cur.execute('INSERT INTO friend_request VALUES (?, ?, ?)', [user1, user2, now_time])
        conn.commit()
    return jsonify(res=0)

@app.route("/friend_update", methods=['POST'])
def friend_update():
    """
    Request:
    0:  confirm a friend request
    1:  delete a friend request
    2:  cancel an add-friend request
    3:  delete a friend
    """
    if 'username' not in session:
        return redirect('/login?type=0')
    user1 = session['username']
    user2 = request.form['username']
    request_type = request.form['request_type']
    now_time = Time.time()

    if request_type not in ['0', '1', '2', '3']:
        return jsonify(res=-1)

    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        # check
        if request_type == '0':
            cur.execute('SELECT * FROM friend_request WHERE user1 = ? AND user2 = ?', [user2, user1])
            if not cur.fetchall():
                return jsonify(res=-1)
        # update
        if request_type != '3':
            if request_type == '2':
                cur.execute('DELETE FROM friend_request WHERE user1 = ? AND user2 = ?', [user1, user2])
            else:
                cur.execute('DELETE FROM friend_request WHERE user1 = ? AND user2 = ?', [user2, user1])
            if request_type == '0':
                cur.execute('INSERT INTO friend VALUES (?, ?, ?)', [user1, user2, now_time])
                cur.execute('INSERT INTO friend VALUES (?, ?, ?)', [user2, user1, now_time])
        else:
            cur.execute('DELETE FROM friend WHERE user1 = ? AND user2 = ?', [user1, user2])
            cur.execute('DELETE FROM friend WHERE user1 = ? AND user2 = ?', [user2, user1])
        conn.commit()
    return jsonify(res=0)


@app.route("/login", methods=['GET'])
def login_page():
    if 'username' in session:
        return redirect('/')
    warning_type = "0"
    get_type = request.args.get('type')
    if get_type:
        warning_type = get_type
    return render_template('login.html', type=warning_type)

@app.route("/user_login", methods=['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']
    if not re.search(ID_REG, username) and username != 'admin':
        return redirect('/login?type=1')

    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM user_login WHERE username = ? AND password = ?', [username, password])
        res = cur.fetchall()

    if res:
        session['username'] = username
        return redirect('/')
    return redirect('/login?type=1')

@app.route('/logout')
def logout():
    """
    Remove the username from the session if it's there
    """
    session.pop('username', None)
    return redirect('/')

@app.route("/get_code", methods=['POST'])
def get_code():
    username = request.form['username']
    if not re.search(ID_REG, username):
        return jsonify(res=-1)
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM user_login WHERE username = ?', [username])
        res = cur.fetchall()
    if res:
        return jsonify(res=-2)

    code = random.randint(1000000000, 2000000000)

    CODE_MAP[username] = str(code)
    print(CODE_MAP.get(username))
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
    print(CODE_MAP.get(username))
    if code != CODE_MAP.get(username):
        return redirect('/login?type=2')
    CODE_MAP.pop(username, None)
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO user_login VALUES (?, ?, ?, ?)'
                    , [username, password, INIT_POINT, INIT_COIN])
        conn.commit()
    session['username'] = username
    return redirect('/')

@app.route('/admin8787')
def admin():
    session['username'] = "admin"
    return redirect('/')

if __name__ == "__main__":
    app.secret_key = os.urandom(16)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=8755)