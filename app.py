from datetime import datetime
from flask import Flask, request, render_template, g
import sqlite3
import base64

app = Flask(__name__)
DATABASE = 'lostItem.db'
lastResult = ""

# 데이터베이스 연결 함수
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# DB에서 이미지 BLOB를 가져와서 base64로 인코딩하는 함수
def read_image_from_db(image_blob):
    return base64.b64encode(image_blob).decode('utf-8')

# 데이터베이스 초기화
with app.app_context():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS items
            (id INTEGER PRIMARY KEY,
            date TEXT,
            type TEXT
            )
            ''')
    conn.commit()

# 기본 라우트
@app.route('/')
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY date DESC LIMIT 1")  # 최신 항목 하나만 가져옵니다.
    latest_item = c.fetchone()
    return render_template('index.html', latest_item=latest_item)

# 페이지네이션 라우트
@app.route('/pagination/<int:page>')
def pagination_route(page):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    return render_template('pagination.html', items=items, current_page=page)

#분실물 저장 라우트
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
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO items (date, type, image) VALUES (?, ?)", (current_date, item))
            conn.commit()
            lastResult = f"분실물 있음 : {result}"
    else:
        lastResult = "분실물 없음"
    print(lastResult)
    return lastResult

# 아이템 조회 라우트
@app.route('/get_item', methods=['GET'])
def get_item():
    conn = get_db()
    c = conn.cursor()

    user_input = request.args.get('user_input')

    if user_input:
        c.execute("SELECT * FROM items WHERE type=?", (user_input,))
        item_details = c.fetchall()

        if len(item_details) == 0:
            return '등록된 분실물이 없습니다.'
        else:
            result_html = '<ul>'
            for item in item_details:
                item_id, date, item_type, image_blob = item
                if image_blob:
                    image_data = read_image_from_db(image_blob)
                    result_html += f'<li>{item_id}, {date}, {item_type}<br><img src="data:image/jpeg;base64,{image_data}" /></li>'
                else:
                    result_html += f'<li>{item}</li>'
            result_html += '</ul>'
            return result_html
    else:
        c.execute("SELECT * FROM items ORDER BY date DESC LIMIT 1")  # 최신 항목 하나만 가져옵니다.
        latest_item = c.fetchone()

        if latest_item is None:
            return '등록된 분실물이 없습니다.'
        else:
            result_html = '<div class="result"><ul>'
            result_html += f'<li>{latest_item}</li>'
            result_html += '</ul></div>'
            return result_html

# 모든 아이템 조회 라우트
@app.route('/get_all_items')
def get_all_items():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    all_items = c.fetchall()
    return render_template('get_all_items.html', get_all_items=all_items)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
