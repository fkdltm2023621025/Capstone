from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'AE54'  # 세션을 위한 비밀 키 설정
bcrypt = Bcrypt(app)

# Flask-Mail 초기화
mail = Mail(app)

# 이메일 설정
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP 서버 주소
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yuncapstone@gmail.com'  # 발신 이메일
app.config['MAIL_PASSWORD'] = 'smqwqttzqhnfmjhv'  # 이메일 비밀번호
mail.init_app(app)

# 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="productdb"
)

# URL과 테이블 컬럼의 매핑
url_column_map = {
    "/LOL": "lol",
    "/PUBG": "pubg",
    "/Overwatch": "overwa",
    "/SA": "sa",
    "/valo": "valo",
    "/CS2": "cs2",
    "/index?name=Faker&table_index=3": "faker",
    "/index?name=ShowMaker&table_index=3": "showmaker",
    "/index?name=Ruler&table_index=2": "ruler",
    "/index?name=Chovy&table_index=2": "chovy",
    "/index?name=Oner&table_index=2": "oner",
    "/index?name=BJ피오&table_index=3": "pio",
    "/index?name=BJ로키&table_index=3": "roki",
    "/index?name=Seoul&table_index=2": "seoul",
    "/index?name=BJ%20이노닉스&table_index=2": "ionix",
    "/index?name=Salute&table_index=2": "salute",
    "/index?name=Profit&table_index=3": "profit",
    "/index?name=Ryujehong&table_index=2": "ryuje",
    "/index?name=JJoNak&table_index=2": "jjonak",
    "/index?name=Geguri&table_index=1": "geguri",
    "/index?name=김효종&table_index=2": "hyojong",
    "/index?name=syukmanGod&table_index=1": "syukman",
    "/index?name=BJ%20ReileyT^T&table_index=1": "reiley",
    "/index?name=지훈둥&table_index=2": "hundung",
    "/index?name=멩밍이잉&table_index=2": "mangming",
    "/index?name=나실인&table_index=1": "nasil",
    "/index?name=Stax&table_index=2": "stax",
    "/index?name=Rb&table_index=3": "rb",
    "/index?name=Buzz&table_index=3": "buzz",
    "/index?name=Lakia&table_index=2": "lakia",
    "/index?name=Meteor&table_index=3": "meteor",
    "/index?name=HeatoN&table_index=2": "heato",
    "/index?name=f0rest&table_index=2": "f0",
    "/index?name=GeT_RiGhT&table_index=3": "getright",
    "/index?name=NEO&table_index=2": "neo",
    "/index?name=markeloff&table_index=3": "mark",
}

# 카테고리별 컬럼 정의
game_categories = ["lol", "pubg", "overwa", "sa", "valo", "cs2"]
lol_players = ["faker", "showmaker", "ruler", "chovy", "oner"]
pubg_players = ["pio", "roki", "seoul", "ionix", "salute"]
overwatch_players = ["profit", "ryuje", "jjonak", "geguri", "hyojong"]
sa_players = ["syukman", "reiley", "hundung", "mangming", "nasil"]
valo_players = ["stax", "rb", "buzz", "lakia", "meteor"]
cs_players = ["heato", "f0", "getright", "neo", "mark"]

cursor = db.cursor(dictionary=True)

# 댓글을 가져오는 함수
def get_comments_for_famous_person(famous_person):
    cursor.execute("""
        SELECT c.comment_id, c.comment, c.likes_count, c.liked_user_ids, u.nick_name 
        FROM comment c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.name = %s
        ORDER BY c.likes_count DESC  -- 좋아요 수 기준 내림차순 정렬
    """, (famous_person,))
    return cursor.fetchall()


# 데이터 관리를 위한 클래스
class ProductRecommender:
    # 생성자: 클래스가 초기화될 때 호출됨
    def __init__(self):
        self.table_names = ['star', 'mainstream', 'highend', 'flagship']  # 사용할 데이터베이스 테이블 이름 리스트
        self.current_table = 'mainstream'  # 기본 테이블을 'mainstream'으로 설정
        self.load_products()  # 초기화 시 제품 데이터를 로드

    # 카테고리 분류 및 TF-IDF 행렬 생성 ( TF - IDF 텍스트의 키워드를 기반으로 핵심내용 추출 )
    def load_products(self):
        cursor.execute(f"SELECT * FROM {self.current_table}")  # 현재 테이블에서 모든 데이터 선택
        self.products = pd.DataFrame(cursor.fetchall())  # 데이터를 DataFrame으로 변환
        self.categories = self.products['카테고리'].unique()  # 카테고리 레이블 리스트 생성
        self.products['카테고리'] = self.products['카테고리'].fillna('')  # NaN 값을 빈 문자열로 대체
        self.tfidf = TfidfVectorizer(stop_words='english')  # TF-IDF 벡터라이저 초기화
        self.tfidf_matrix = self.tfidf.fit_transform(self.products['카테고리'])  # 카테고리 데이터를 TF-IDF 행렬로 변환
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)  # 코사인 유사도 행렬 생성

        # => TF-IDF는 정보 검색과 텍스트 마이닝에서 널리 사용되는 가중치 조합 방법 TF-IDF는 단어의 중요도를 평가하여 문서의 특징을 나타내는 데 사용
        # => 즉 카테고리 리스트를 기준으로 잡고 가는것

    # 테이블 선택 업데이트 및 데이터 로드 ( 프로선수, 방송인 선택영역 )
    def update_table_selection(self, table_index):
        self.current_table = self.table_names[table_index]  # 선택된 테이블 이름으로 업데이트
        self.load_products()  # 새 테이블에서 데이터 로드

    # 제품 추천 로직
    def get_recommendations(self, category, num_recommendations=8):
        exact_match_indices = self.products[self.products['카테고리'] == category].index.tolist()  # 정확히 일치하는 카테고리 인덱스 리스트
        related_indices = self.products[self.products['카테고리'].str.contains(category)].index.tolist()  # 카테고리를 포함하는 인덱스 리스트
        final_indices = list(dict.fromkeys(exact_match_indices + related_indices))  # 중복 제거 및 인덱스 결합
        final_indices = final_indices[:num_recommendations]  # 추천 수 제한
        result = self.products.loc[final_indices][['제품', '설명']]  # 추천 제품과 설명을 포함한 DataFrame 생성
        return result.to_dict(orient='records')  # 결과를 딕셔너리 형태로 반환

# ProductRecommender 인스턴스 생성
recommender = ProductRecommender()

# 회원가입 페이지 라우트
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        nick_name = request.form['nick_name']
        user_id = request.form['id']
        password = request.form['password']
        email = request.form['email']
        admin_user = 0  # 기본적으로 일반 유저로 설정

        # 비밀번호 해시화 ( 현재 사용하지 않음 )
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # 중복 확인 쿼리
        cursor.execute("SELECT * FROM users WHERE id = %s OR email = %s", (user_id, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            alert_message = "[회원가입 실패] 아이디 또는 이메일이 이미 사용 중입니다."
            return render_template('signup.html', alert_message=alert_message)
        
        # 중복 확인 쿼리2
        cursor.execute("SELECT * FROM users WHERE nick_name = %s", (nick_name,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            alert_message = "[회원가입 실패] 이미 사용중인 닉네임입니다."
            return render_template('signup.html', alert_message=alert_message)

        # 중복 확인 쿼리3
        cursor.execute("SELECT * FROM deleteusers WHERE delete_id = %s", (user_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            alert_message = "[회원가입 실패] 사용 불가능한 아이디 입니다."
            return render_template('signup.html', alert_message=alert_message)

        # 사용자 정보를 데이터베이스에 삽입
        cursor.execute("""
            INSERT INTO users (name, nick_name, id, password, email, admin_user)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, nick_name, user_id, hashed_password, email, admin_user))
        db.commit()

        return redirect(url_for('index'))
    return render_template('signup.html')

# 로그인 페이지 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']

        # 사용자 정보 조회
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        # 사용자 검증
        if user and bcrypt.check_password_hash(user['password'], password): # 사용자 입력 PW 비교
            session['user_id'] = user['user_id']
            session['id'] = user['id']
            session['user_name'] = user['name']
            session['user_nick_name'] = user['nick_name']
            session['user_email'] = user['email']
            session['admin_user'] = user['admin_user']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', alert_message="[로그인 실패] 아이디나 비밀번호가 잘못되었습니다.")
    return render_template('login.html')

# 로그아웃 라우트
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 관리자 페이지 라우트
@app.route("/adminPage")
def adminPage():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template("adminPage.html", users=users)

# 관리자 유저 추적
@app.route("/access_url", methods=["POST"])
def access_url():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session["user_id"]
    pathname = request.json.get("pathname")
    search = request.json.get("search")
    url_accessed = pathname+search

    if pathname and search:
        print(url_accessed)
        print(pathname+search)

    # URL이 url_column_map에 있는지 확인
    if url_accessed in url_column_map:
        column_name = url_column_map[url_accessed]

        # user_id가 있는지 확인
        cursor.execute("SELECT * FROM urlconnection WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            print(url_accessed)
            print(column_name)
            # user_id가 있으면 해당 컬럼 값 증가
            update_query = f"UPDATE urlconnection SET {column_name} = {column_name} + 1 WHERE user_id = %s"
            cursor.execute(update_query, (user_id,))
        else:
            print(url_accessed)
            print(column_name)
            # user_id가 없으면 새 레코드 생성 후 해당 컬럼 값 증가
            columns = ", ".join(url_column_map.values())
            placeholders = ", ".join("0" for _ in url_column_map)
            insert_query = f"INSERT INTO urlconnection (user_id, {columns}) VALUES (%s, {placeholders})"
            cursor.execute(insert_query, (user_id,))
            cursor.execute(
                f"UPDATE urlconnection SET {column_name} = 1 WHERE user_id = %s",
                (user_id,),
            )

        db.commit()
        return jsonify(
            {"message": f"{column_name} count incremented for user_id {user_id}"}
        )
    else:
        return jsonify({"error": "URL not recognized"}), 400


@app.route("/adminPage/category-stats", methods=["GET"])
def get_category_stats():
    stats = {}
    categories = {
        "game_categories": game_categories,
        "lol_players": lol_players,
        "pubg_players": pubg_players,
        "overwatch_players": overwatch_players,
        "sa_players": sa_players,
        "valo_players": valo_players,
        "cs_players": cs_players,
    }

    for category_name, columns in categories.items():
        stats[category_name] = {}
        for column in columns:
            cursor.execute(f"SELECT SUM({column}) as total FROM urlconnection")
            result = cursor.fetchone()
            stats[category_name][column] = result["total"] if result["total"] else 0

    return jsonify(stats) 

# 댓글 데이터를 가져오는 라우트
@app.route("/adminPage/get_comment", methods=["POST"])
def get_comment():
    user_id = request.json.get("user_id")  # AJAX 요청에서 전달받은 
    print(user_id)
    print(type(user_id))

    query = """
        SELECT comment.comment_id, comment.name, comment.comment
        FROM comment
        JOIN users ON users.user_id = comment.user_id
        WHERE comment.user_id = %s
    """
    cursor.execute(query, (user_id,))
    comments = cursor.fetchall()

    return jsonify(comments)  # JSON 형태로 반환하여 JS에서 처리 가능하도록 함


# 닉네임 변경 요청 처리 라우트
@app.route("/adminPage/change_nickname", methods=["POST"])
def change_nickname():
    user_id = int(request.json.get("user_id"))
    new_nickname = request.json.get("new_nickname")

    cursor.execute(
        "UPDATE users SET nick_name = %s WHERE user_id = %s", (new_nickname, user_id)
    )
    db.commit()

    return jsonify({"status": "success"})

# 탈퇴 요청 처리 라우트
@app.route("/adminPage/delete_user", methods=["POST"])
def delete_user():
    user_id = int(request.json.get("user_id"))

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    id_data = cursor.fetchone()

    cursor.execute("INSERT INTO deleteusers (delete_id) VALUES (%s)", (id_data['id'],))
    cursor.execute("DELETE FROM users WHERE id = %s", (id_data['id'],))
    db.commit()

    return jsonify({"status": "success"})

# 닉네임 변경
@app.route('/change_nick', methods=['POST'])
def change_nick():
    if request.method == 'POST':
        new_nick = request.form['nick_change']
        cursor = db.cursor()
        
        # 중복 확인 쿼리
        cursor.execute("SELECT * FROM users WHERE nick_name = %s", (new_nick,))
        existing_user = cursor.fetchone()

        if existing_user:
            alert_message = "이 닉네임은 이미 사용중이거나 사용 할 수 없는 닉네임 입니다."
            return render_template('Mypage.html', alert_message=alert_message)

        cursor.execute("UPDATE users SET nick_name = %s WHERE id = %s", (new_nick, session['id']))
        db.commit()
        cursor.close()
        session['user_nick_name'] = new_nick
        return render_template('Mypage.html', alert_message="닉네임 변경에 성공했습니다.")
    return render_template('Mypage.html')

# 이메일 변경
@app.route('/change_email', methods=['POST'])
def change_email():
    if request.method == 'POST':
        new_email = request.form['email_change']
        cursor = db.cursor()
        
        # 중복 확인 쿼리
        cursor.execute("SELECT * FROM users WHERE email = %s", (new_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            alert_message = "이 이메일은 이미 사용중입니다."
            return render_template('Mypage.html', alert_message=alert_message)

        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, session['id']))
        db.commit()
        cursor.close()
        session['user_email'] = new_email
        return render_template('Mypage.html', alert_message="이메일 변경에 성공했습니다.")
    return render_template('Mypage.html')

# 회원 탈퇴
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if request.method == 'POST':
        chk_text = request.form['delete_chk']
        cursor = db.cursor()

        if chk_text == '회원탈퇴':
            cursor.execute("DELETE FROM users WHERE id = %s", (session['id'],))
            cursor.execute("INSERT INTO deleteusers VALUES(%s)", (session['id'],))
            db.commit()
            cursor.close()
            session.clear()
            alert_message = "탈퇴 처리 되었습니다. 이용해 주셔서 감사합니다."
            delete_success = True
            return render_template('delete_user.html', alert_message=alert_message, delete_success=delete_success)

        else:
            alert_message = "입력이 잘못되었습니다. 다시 시도해 주십시오."
            delete_success = False
            return render_template('delete_user.html', alert_message=alert_message, delete_success=delete_success)
            
# PW변경
@app.route('/pw_change', methods=['POST'])
def pw_change():
    if request.method == 'POST':
        new_pw = request.form['new_pw']
        new_pw_chk = request.form['new_pw_chk']

        if new_pw == new_pw_chk:
            # 새 비밀번호 해시화
            hashed_new_pw = bcrypt.generate_password_hash(new_pw).decode('utf-8')

            # 해시화된 비밀번호로 업데이트
            cursor = db.cursor()  # db 연결 커서 생성
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_pw, session['id']))
            db.commit()  # 변경 사항 커밋
            cursor.close()  # 커서 닫기
            return render_template('Mypage.html', alert_message="비밀번호 변경에 성공했습니다.")
        else:
            return render_template('Mypage.html', alert_message="[비밀번호 변경 실패] PW를 다르게 입력했습니다.")
    return render_template('Mypage.html')

# PW변경 ( 이메일 기준 )
@app.route('/pw_change_email', methods=['POST'])
def pw_change_email():
    if request.method == 'POST':
        new_pw = request.form['new_pw']
        new_pw_chk = request.form['new_pw_chk']

        if new_pw == new_pw_chk:
            # 새 비밀번호 해시화
            hashed_new_pw = bcrypt.generate_password_hash(new_pw).decode('utf-8')

            # 해시화된 비밀번호로 업데이트
            cursor = db.cursor()  # db 연결 커서 생성
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_new_pw, session['email']))
            db.commit()  # 변경 사항 커밋
            cursor.close()  # 커서 닫기
            session.pop('email')
            return render_template('home.html', alert_message="비밀번호 변경에 성공했습니다.")
        else:
            return render_template('account_result_pw.html', alert_message="[비밀번호 변경 실패] PW를 다르게 입력했습니다.")
    return render_template('home.html')

# ID PW 찾기 페이지 라우트
@app.route('/findAccount', methods=['GET', 'POST'])
def findAccount():
    return render_template('findAccount.html')

# ID / PW 찾는 로직
@app.route('/find_id', methods=['POST'])
def find_id():
    email = request.form['email']

    # 데이터베이스에서 이메일 확인
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        random_number = str(random.randint(10000, 99999))  # 랜덤 5자리 숫자 생성

        # 이메일 전송
        msg = Message('장비좀봐줄래? ID 분실 확인 메일', sender='장비좀봐줄래?', recipients=[email])
        msg.body = f'인증번호: {random_number} 를 인증확인 창에 기입해 주세요.'
        mail.send(msg)

        # 세션이나 다른 방법으로 랜덤 숫자를 저장
        session['verification_code'] = random_number
        session['email'] = email  # 추가: 이메일도 세션에 저장
        return render_template('verify_code.html', action='find_id')
    
    return render_template('findAccount.html', alert_message = "해당 이메일은 존재하지 않는 이메일입니다.")

@app.route('/find_pw', methods=['POST'])
def find_pw():
    email = request.form['email']

    # 데이터베이스에서 이메일 확인
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        random_number = str(random.randint(10000, 99999))  # 랜덤 5자리 숫자 생성

        # 이메일 전송
        msg = Message('장비좀봐줄래? PW 분실 확인 메일', sender='장비좀봐줄래?', recipients=[email])
        msg.body = f'인증번호: {random_number} 를 인증확인 창에 기입해 주세요.'
        mail.send(msg)

        # 세션이나 다른 방법으로 랜덤 숫자를 저장
        session['verification_code'] = random_number
        session['email'] = email  # 추가: 이메일도 세션에 저장
        return render_template('verify_code.html', action='find_pw')

    return render_template('findAccount.html', alert_message = "해당 이메일은 존재하지 않는 이메일입니다.")

# 입력된 코드 확인 및 ID/PW 반환 페이지 라우트
@app.route('/verify_codes', methods=['POST'])
def verify_codes():
    input_code = request.form['code']
    action = request.form['action']

    if input_code == session.get('verification_code'):
        if action == 'find_id':
            cursor.execute("SELECT id FROM users WHERE email = %s", (session.get('email'),))
            user = cursor.fetchone()
            return render_template('account_result.html', find_account_id = '회원님의 ID 는 ' + user['id'] + ' 입니다.')# ID 반환
            #return f"Your ID is: {user['id']}"  # ID 반환
        elif action == 'find_pw':
            cursor.execute("SELECT password FROM users WHERE email = %s", (session.get('email'),))
            user = cursor.fetchone()
            return render_template('account_result_pw.html', find_account_id = '비밀번호 변경')

    return "잘못된 접근입니다."

# 내 정보
@app.route('/mypage')
def mypage():
    return render_template('Mypage.html')

# 회원탈퇴 페이지
@app.route('/mypage_delete')
def mypage_delete():
    alert_message = '경고! 회원탈퇴 페이지 입니다.'
    return render_template('delete_user.html', alert_message=alert_message)

# 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('home.html')

# League of Legends 페이지 라우트
@app.route('/LOL')
def league():
    return render_template('League_Of_Legends.html')

# PUBG 페이지 라우트
@app.route('/PUBG')
def PUBG():
    return render_template('PUBG.html')

# Overwatch 페이지 라우트
@app.route('/Overwatch')
def Overwatch():
    return render_template('Overwatch.html')

# CounterStrike2 페이지 라우트
@app.route('/CS2')
def CounterStrike2():
    return render_template('CounterStrike2.html')

# CounterStrike2 페이지 라우트
@app.route('/SA')
def SA():
    return render_template('Suddenattack.html')

# CounterStrike2 페이지 라우트
@app.route('/valo')
def Valo():
    return render_template('Valorant.html')

# index.html 호출 시 유명인의 제품 정보를 가져오는 기능 추가
@app.route('/index')
def index_with_star():
    famous_person = request.args.get('name')
    table_index = int(request.args.get('table_index', 0))  # 기본값은 0으로 설정

    # 유명인 정보 가져오기
    cursor.execute(f"SELECT * FROM star WHERE name = '{famous_person}'")
    famous_person_data = cursor.fetchone()
    
    # 댓글 가져오기
    comments = get_comments_for_famous_person(famous_person)

    return render_template('index.html', famous_person=famous_person, famous_person_data=famous_person_data, categories=recommender.categories, comments=comments)

# 이미지 선택값 받아오기
@app.route('/update_data_select', methods=['POST'])
def update_data_select():
    data = request.get_json()
    table_index = int(data.get('value'))
    recommender.update_table_selection(table_index)
    return jsonify({'status': 'success', 'message': 'Table selection updated successfully.'})

# index.html 의 form action 태그의 내용
@app.route('/recommend', methods=['POST'])
def recommend():
    category = request.form['category']
    recommended_products = recommender.get_recommendations(category)
    
    # 유명인의 제품 정보를 가져오는 로직 추가
    famous_person = request.args.get('name')
    famous_person_data = None  # 기본값으로 설정
    comments = []
    if famous_person:
        cursor.execute(f"SELECT * FROM star WHERE name = '{famous_person}'")
        famous_person_data = cursor.fetchone()
        
        # 댓글 가져오기
        comments = get_comments_for_famous_person(famous_person)
    
    return render_template('index.html', famous_person=famous_person, famous_person_data=famous_person_data, product_title=category, recommended_products=recommended_products, categories=recommender.categories, comments=comments)

# 댓글 저장 라우트
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    famous_person = request.form['famous_person']
    comment = request.form['comment']
    user_id = session.get('user_id')  # 세션에 로그인된 유저의 고유번호

    if user_id and famous_person and comment:
        cursor.execute("""
            INSERT INTO comment (name, user_id, comment)
            VALUES (%s, %s, %s)
        """, (famous_person, user_id, comment))
        db.commit()

    return jsonify({'success': '댓글이 추가되었습니다.'}), 200

# 댓글 좋아요
@app.route('/like_comment', methods=['POST'])
def like_comment():
    comment_id = request.form['comment_id']
    user_id = session.get('user_id')  # 세션에서 로그인된 유저 ID 가져오기

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    # 댓글 정보 가져오기
    cursor.execute("SELECT likes_count, liked_user_ids FROM comment WHERE comment_id = %s", (comment_id,))
    comment = cursor.fetchone()

    if comment:
        liked_user_ids = comment['liked_user_ids'].split(',') if comment['liked_user_ids'] else []
        
        # 이미 좋아요를 누른 유저인 경우 처리
        if str(user_id) in liked_user_ids:
            return jsonify({'error': '이미 좋아요를 누른 댓글입니다.'}), 400

        # 좋아요 추가
        liked_user_ids.append(str(user_id))  # 유저 ID 추가
        new_liked_user_ids = ','.join(liked_user_ids)
        new_likes_count = comment['likes_count'] + 1

        # 댓글 업데이트
        cursor.execute("""
            UPDATE comment 
            SET likes_count = %s, liked_user_ids = %s 
            WHERE comment_id = %s
        """, (new_likes_count, new_liked_user_ids, comment_id))
        db.commit()

        return jsonify({'success': '좋아요가 반영되었습니다.'}), 200
    else:
        return jsonify({'error': '댓글이 존재하지 않습니다.'}), 404


# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') # 배포버전에선 debug=false 로 올린다.
