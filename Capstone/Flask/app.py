from flask import Flask, request, jsonify, render_template
import pandas as pd
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)

# 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="4528",
    database="productdb"
)

cursor = db.cursor(dictionary=True)

# 데이터 관리를 위한 클래스
class ProductRecommender:
    # 데이터베이스의 테이블 선택( 기본 products )
    def __init__(self):
        self.table_names = ['star', 'products', 'another_products']
        self.current_table = 'products'
        self.load_products()

    # 카테고리 분류
    def load_products(self):
        cursor.execute(f"SELECT * FROM {self.current_table}")
        self.products = pd.DataFrame(cursor.fetchall())
        self.categories = self.products['카테고리'].unique()
        self.products['카테고리'] = self.products['카테고리'].fillna('')
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.products['카테고리'])
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)

    def update_table_selection(self, table_index):
        self.current_table = self.table_names[table_index]
        self.load_products()

    def get_recommendations(self, category, num_recommendations=10):
        exact_match_indices = self.products[self.products['카테고리'] == category].index.tolist()
        related_indices = self.products[self.products['카테고리'].str.contains(category)].index.tolist()
        final_indices = list(dict.fromkeys(exact_match_indices + related_indices))
        final_indices = final_indices[:num_recommendations]
        result = self.products.loc[final_indices][['제품', '설명']]
        return result.to_dict(orient='records')

recommender = ProductRecommender()

# index.html 호출 시 유명인의 제품 정보를 가져오는 기능 추가
@app.route('/index')
def index():
    famous_person = request.args.get('name')
    table_index = int(request.args.get('table_index', 0))  # 기본값은 0으로 설정

    if table_index == 1:  # star 테이블일 경우
        cursor.execute(f"SELECT * FROM Star WHERE name = '{famous_person}'")
        famous_person_data = cursor.fetchone()
        return render_template('index.html', famous_person=famous_person, famous_person_data=famous_person_data, categories=recommender.categories)
    else:
        # 다른 테이블에서의 처리 추가
        pass

# img_click.js 의 이미지 선택값 받아오기
@app.route('/update_data_select', methods=['POST'])
def update_data_select():
    data = request.get_json()
    table_index = int(data.get('value'))
    recommender.update_table_selection(table_index)
    return jsonify({'status': 'success', 'message': 'Table selection updated successfully.'})

# index.html 의 from action 태그의 내용
@app.route('/recommend', methods=['POST'])
def recommend():
    category = request.form['category']
    recommended_products = recommender.get_recommendations(category)
    
    # 유명인의 제품 정보를 가져오는 로직 추가
    famous_person = request.args.get('name')
    if famous_person:
        cursor.execute(f"SELECT * FROM Star WHERE name = '{famous_person}'")
        famous_person_data = cursor.fetchone()
    else:
        famous_person_data = None
    
    return render_template('index.html', famous_person=famous_person, famous_person_data=famous_person_data, product_title=category, recommended_products=recommended_products, categories=recommender.categories)

# home.html 호출
@app.route('/')
def about():
    return render_template('home.html')

# LOL 사이트 호출
@app.route('/LOL')
def league():
    return render_template('League_Of_Legends.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
