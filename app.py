#db 뷰어
#https://sqliteviewer.app/
from flask import Flask, request, render_template, g
import sqlite3
from PIL import Image

app = Flask(__name__)
DATABASE = 'example.db'

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
              image BLOB,
              type TEXT)
              ''')
    conn.commit()

# 이미지를 바이너리 데이터로 변환하여 데이터베이스에 저장
def convert_image_to_binary(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

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
    conn = get_db()
    c = conn.cursor()

    item_info = request.json

    image_binary = convert_image_to_binary(item_info['image']) #이미지 -> 바이너리

    c.execute("INSERT INTO items (image, type) VALUES (?, ?)", (image_binary, item_info['type']))
    conn.commit()

    return 'Item stored successfully!'

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

if __name__ == '__main__':
    app.run(debug=True)
