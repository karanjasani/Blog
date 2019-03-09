import sqlite3

conn = sqlite3.connect('blogdatabase.db')

c = conn.cursor()

c.execute(""" Create table if not exists users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    password TEXT,
                    create_time DATETIME,
                    update_time DATETIME) """)

c.execute(""" Create table if not exists article (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    user_id INTEGER,
                    create_time DATETIME,
                    update_time DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)) """)

c.execute(""" Create table if not exists comment (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comment_content TEXT,
                    user TEXT,
                    article_id INTEGER,
                    create_time DATETIME,
                    update_time DATETIME,
                    FOREIGN KEY (article_id) REFERENCES article(article_id)) """)

c.execute(""" Create table if not exists tag_head (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_name TEXT,
                    tag_frequency TEXT,
                    create_time DATETIME,
                    update_time DATETIME) """)

c.execute(""" Create table if not exists tag_detail (
                    article_id INTEGER,
                    tags TEXT,
                    create_time DATETIME,
                    update_time DATETIME,
                    FOREIGN KEY (article_id) REFERENCES article(article_id)) """)

conn.commit()

conn.close()
