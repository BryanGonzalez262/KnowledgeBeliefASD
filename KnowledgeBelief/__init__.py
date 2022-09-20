import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_recaptcha import ReCaptcha
from flask_migrate import Migrate
from flask_mail import Mail
import json


app = Flask(__name__)


with open("KnowledgeBelief/config.json") as config_file:
    config = json.load(config_file)

app.config['SECRET_KEY'] = config.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "False"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = "False"
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['RECAPTCHA_SITE_KEY'] = config.get("RECAPTCHA_SITE_KEY")
app.config['RECAPTCHA_SECRET_KEY'] = config.get("RECAPTCHA_SECRET_KEY")
app.config['MAIL_SERVER'] = config.get("MAIL_SERVER")
app.config['MAIL_PORT'] = config.get("MAIL_PORT")
app.config['STUDY_MAIL_SUBJECT'] = config.get("STUDY_MAIL_SUBJECT")
app.config['STUDY_MAIL_SENDER'] = config.get("STUDY_MAIL_SENDER")
app.config['MAIL_USE_TLS'] = "True"
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")




db = SQLAlchemy(app)
cors = CORS(app)
bootstrap = Bootstrap(app)
recaptcha = ReCaptcha(app)
mail = Mail(app)
migrate = Migrate(app, db)



from . import views
if __name__ == '__main__':
    #app.run(ssl_context=('./cert.pem', './key.pem'))
    app.run()