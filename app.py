from flask import Flask, request, redirect, render_template_string
import pymysql

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'hw_db'
}

def get_db_connection():
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def get_all_topics():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM topics')
            result = cursor.fetchall()
    finally:
        connection.close()
    return result

def get_topic_by_id(topic_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM topics WHERE id = %s', (topic_id,))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result

def insert_topic(title, body):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO topics (title, body) VALUES (%s, %s)', (title, body))
        connection.commit()
    finally:
        connection.close()

def update_topic(topic_id, title, body):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE topics SET title = %s, body = %s WHERE id = %s', (title, body, topic_id))
        connection.commit()
    finally:
        connection.close()

def delete_topic(topic_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM topics WHERE id = %s', (topic_id,))
        connection.commit()
    finally:
        connection.close()

def template(contents, content, id=None):
    contextUI = ''
    if id is not None:
        contextUI = f'''
            <li><a href="/update/{id}/">수정</a></li>
            <li><form action="/delete/{id}/" method="POST"><input type="submit" value="삭제"></form></li>
        '''
    return f'''<!doctype html>
    <html>
        <head>
            <link rel="stylesheet" href="/static/styles.css">
        </head>
        <body>
            <h1><a href="/">WEB</a></h1>
            <form action="/search/" method="GET">
                <p><input type="text" name="query" placeholder="검색..."></p>
                <p><input type="submit" value="검색"></p>
            </form>
            <ol>
                {contents}
            </ol>
            {content}
            <ul>
                <li><a href="/create/">글 쓰기</a></li>
                {contextUI}
            </ul>
        </body>
    </html>
    '''

@app.route('/')
def index():
    topics = get_all_topics()
    contents = ''.join(f'<li><a href="/read/{topic["id"]}/">{topic["title"]}</a></li>' for topic in topics)
    return template(contents, '<h2>Welcome to my WebSite</h2>')

@app.route('/read/<int:id>/')
def read(id):
    topic = get_topic_by_id(id)
    if topic:
        return template(
            ''.join(f'<li><a href="/read/{t["id"]}/">{t["title"]}</a></li>' for t in get_all_topics()),
            f'<h2>{topic["title"]}</h2>{topic["body"]}',
            id
        )
    return 'Topic not found', 404

@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'GET': 
        content = '''
            <form action="/create/" method="POST">
                <p><input type="text" name="title" placeholder="title"></p>
                <p><textarea name="body" placeholder="body"></textarea></p>
                <p><input type="submit" value="create"></p>
            </form>
        '''
        return template(''.join(f'<li><a href="/read/{t["id"]}/">{t["title"]}</a></li>' for t in get_all_topics()), content)
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        insert_topic(title, body)
        return redirect('/')

@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update(id):
    if request.method == 'GET':
        topic = get_topic_by_id(id)
        if topic:
            content = f'''
                <form action="/update/{id}/" method="POST">
                    <p><input type="text" name="title" placeholder="title" value="{topic["title"]}"></p>
                    <p><textarea name="body" placeholder="body">{topic["body"]}</textarea></p>
                    <p><input type="submit" value="update"></p>
                </form>
            '''
            return template(''.join(f'<li><a href="/read/{t["id"]}/">{t["title"]}</a></li>' for t in get_all_topics()), content)
        return 'Topic not found', 404
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        update_topic(id, title, body)
        return redirect('/')

@app.route('/delete/<int:id>/', methods=['POST'])
def delete(id):
    delete_topic(id)
    return redirect('/')

@app.route('/search/')
def search():
    query = request.args.get('query', '').lower()
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM topics WHERE LOWER(title) LIKE %s OR LOWER(body) LIKE %s', (f'%{query}%', f'%{query}%'))
            search_results = cursor.fetchall()
    finally:
        connection.close()
    
    if not search_results:
        search_results_content = '<p>결과를 찾을 수 없습니다.</p>'
    else:
        search_results_content = '<ol>' + ''.join(f'<li><a href="/read/{topic["id"]}/">{topic["title"]}</a></li>' for topic in search_results) + '</ol>'
    
    return template(''.join(f'<li><a href="/read/{t["id"]}/">{t["title"]}</a></li>' for t in get_all_topics()), search_results_content)

if __name__ == '__main__':
    app.run(debug=True)
