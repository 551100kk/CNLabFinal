import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''
        CREATE TABLE `user_login` (
            `username`  text NOT NULL,
            `password`  text NOT NULL,
            PRIMARY KEY(`username`)
            )''')

c.execute('''
        INSERT INTO user_login VALUES ('admin', 'myadmin')
        ''')

# c.execute("SELECT * FROM user_login")

conn.commit()
conn.close()

