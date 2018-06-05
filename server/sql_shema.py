import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''
        CREATE TABLE IF NOT EXISTS `user_login` (
            `username`  text NOT NULL,
            `password`  text NOT NULL,
            `point`     INTEGER NOT NULL,
            `coin`      INTEGER NOT NULL,
            PRIMARY KEY(`username`)
        )''')
c.execute('''
        CREATE TABLE IF NOT EXISTS `friend` (
            `user1` TEXT NOT NULL,
            `user2` TEXT NOT NULL,
            `time`  INTEGER NOT NULL,
            PRIMARY KEY(`user2`,`user1`),
            FOREIGN KEY(user1) REFERENCES user_login(username),
            FOREIGN KEY(user2) REFERENCES user_login(username)
        );''')
c.execute('''
        CREATE TABLE IF NOT EXISTS `friend_request` (
            `user1` TEXT NOT NULL,
            `user2` TEXT NOT NULL,
            `time`  INTEGER NOT NULL,
            PRIMARY KEY(`user2`,`user1`),
            FOREIGN KEY(user1) REFERENCES user_login(username),
            FOREIGN KEY(user2) REFERENCES user_login(username)
        );''')
c.execute('''
        INSERT INTO user_login VALUES ('admin', 'myadmin', 1000, 100)
        ''')

# c.execute("SELECT * FROM user_login")

conn.commit()
conn.close()

    