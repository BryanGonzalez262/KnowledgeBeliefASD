from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_recaptcha import ReCaptcha
from flask_migrate import Migrate
import json


app = Flask(__name__)
config_dir = "config.json"

with open("KnowledgeBelief/config.json") as config_file:
    config = json.load(config_file)

app.config['SECRET_KEY'] = config.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = config.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "False"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = "False"
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['RECAPTCHA_SITE_KEY'] = config.get("RECAPTCHA_SITE_KEY")
app.config['RECAPTCHA_SECRET_KEY'] = config.get("RECAPTCHA_SECRET_KEY")



db = SQLAlchemy(app)
cors = CORS(app)
bootstrap = Bootstrap(app)
recaptcha = ReCaptcha(app)
migrate = Migrate(app, db)


from . import views
if __name__ == '__main__':
    #app.run(ssl_context=('./cert.pem', './key.pem'))
    app.run()