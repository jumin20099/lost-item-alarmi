#db 뷰어
#https://sqliteviewer.app/
from flask import Flask, request, render_template, g
import sqlite3
from PIL import Image

app = Flask(__name__)
DATABASE = 'lostItem.db'
lastResult = ""

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

with app.app_context():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS items
              (id INTEGER PRIMARY KEY,
              type TEXT)
              ''')
    conn.commit()

@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    return render_template('index.html', items=items)

@app.route('/pagination/<int:page>')
def pagination_route(page):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    return render_template('pagination.html', items=items, current_page=page)


@app.route('/store_item', methods=['POST'])
def store_item():
    global lastResult
    conn = get_db()
    c = conn.cursor()

    getData = request.get_data("data").decode("utf-8")

    objs = ["person", "cell phone", "backpack", "earphone", "wallet"]
    result = []
    for obj in objs:
        if obj in getData:
            result.append(obj)

    if "person" not in result:
        for item in result:
            c.execute("INSERT INTO items (type) VALUES (?)", (item,))
            conn.commit()
            lastResult = f"분실물 있음 : {result}"
    else:
        lastResult = "분실물 없음"
    print(lastResult)
    return lastResult
    


# 여기가 웹사이트 접속했을때 출력 되는 부분 시작
@app.route('/get_item', methods=['GET'])
def get_item():
    conn = get_db()
    c = conn.cursor()

    user_input = request.args.get('user_input')

    c.execute("SELECT * FROM items WHERE type=?", (user_input,))
    item_details = c.fetchall()

    if len(item_details) == 0:
        return '일치하는 데이터가 없습니다.'
    else:
        return str(item_details)
# 끝점


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)