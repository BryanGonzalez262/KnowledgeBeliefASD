from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_recaptcha import ReCaptcha
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfkjfsdlf'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///knwlg_blf.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['RECAPTCHA_SITE_KEY'] = 'XXXXX-B--M'
app.config['RECAPTCHA_SECRET_KEY'] = 'XXXXXXZy_'


db = SQLAlchemy(app)
cors = CORS(app)
bootstrap = Bootstrap(app)
recaptcha = ReCaptcha(app)
migrate = Migrate(app, db)


from . import views
if __name__ == '__main__':
    #app.run(ssl_context=('./cert.pem', './key.pem'))
    app.run()