# -*- coding: utf-8 -*-
from flask import Flask, request, Response, abort, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
from flask_firebase import FirebaseAuth

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

app.config['FIREBASE_API_KEY'] = "<The API key.>"
app.config['FIREBASE_PROJECT_ID'] = "<The project identifier, eg. foobar.>"
app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'] = "email,facebook,github,google,twitter" # Comma-separated list of enabled providers.
app.debug=True
auth = FirebaseAuth(app)
app.register_blueprint(auth.blueprint, url_prefix='/auth')

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
users = {
    1: User(1, "user01@example.com", "password"),
    2: User(2, "user02@example.com", "password")
}

# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def home():
    return Response("home: <a href='/login/'>Login</a> <a href='/protected/'>Protected</a> <a href='/logout/'>Logout</a>")

# ログインしないと表示されないパス
@app.route('/protected/')
@login_required
def protected():
    return Response('''
    protected<br />
    <a href="/logout/">logout</a>
    ''')

# ログインパス
@app.route('/login/')
@login_required
def login():
    return redirect("/")

# ログアウトパス
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/")

@login_manager.unauthorized_handler
def authentication_required():
    return redirect(auth.url_for('widget', mode='select', next=request.url))

@auth.production_loader
def production_sign_in(token):
    # ユーザーチェック
    if(token in user_check):
        # ユーザーが存在した場合はログイン
        login_user(users.get(user_check[token]["id"]))


@auth.development_loader
def development_sign_in(email):
    # ユーザーチェック
    #if(email in user_check):
        # ユーザーが存在した場合はログイン
        login_user(users.get(user_check[email]["id"]))

if __name__ == '__main__':
    app.run(host="localhost",port=8080,debug=True)
