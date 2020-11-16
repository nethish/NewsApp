from flask import Flask, redirect, request, url_for, session, render_template
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import requests
from oauthlib.oauth2 import WebApplicationClient
import db
import os
import json
from user import User


GOOGLE_CLIENT_ID = '569030689502-3e50o9imhdsj8iahsaqqte3a5oudirva.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'dt6bh8y7g9V15ka8WPAbl9Bn'
DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
PROVIDER_CONFIG = requests.get(DISCOVERY_URL).json()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

client = WebApplicationClient(GOOGLE_CLIENT_ID)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(email):
    u = db.get_user(email)
    if not u:
        return None
    user = User(u[0], u[1], u[2])
    return user

@app.route('/', methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('news'))
    else:
        return render_template('base.htm')

@app.route('/login', methods=['GET'])
def login():
    auth_endpoint = PROVIDER_CONFIG['authorization_endpoint']
    auth_request = client.prepare_request_uri(auth_endpoint, request.base_url + '/callback', ['openid', 'email', 'profile'])
    return redirect(auth_request)

@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    token_endpoint = PROVIDER_CONFIG['token_endpoint']
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = PROVIDER_CONFIG['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    info = userinfo_response.json()
    if info.get("email_verified"):
        email = info['email']
        picture = info['picture']
        name = info['name']
    else:
        return "User email not available or not verified by Google.", 400

    user = User(email, name, picture)
    if not db.registered_user(user):
        db.create_user(user)

    login_user(user)
    return redirect(url_for("news"))

@app.route('/news', methods=['GET'])
@login_required
def news():
    latest_news = db.get_latest_news()
    print(latest_news)
    return render_template('news.htm', user=current_user, news=latest_news)

@app.route('/create', methods=['POST'])
@login_required
def create():
    new = request.form['mynews']
    db.create_news(current_user, new)
    return redirect(url_for('news'))

@app.route('/delete/<newsid>', methods=['DELETE'])
@login_required
def delete(newsid):
    db.delete_news(newsid)
    return redirect(url_for('mynews'))

@app.route('/mynews', methods=['GET'])
@login_required
def mynews():
    news = db.get_news(current_user)
    return render_template('mynews.htm', news = news)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(ssl_context="adhoc")
