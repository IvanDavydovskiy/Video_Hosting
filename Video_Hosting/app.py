import os


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from os import getenv


load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'media'
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = getenv('RECAPTCHA_PRIVATE_KEY')
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = getenv('EMAIL_PORT')
app.config['MAIL_USERNAME'] = getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
cache = Cache(app)
email = Mail(app)


preview_uploads_dir = os.path.join(app.root_path, 'static/previews')
video_uploads_dir = os.path.join(app.root_path, 'static/videos')


serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
