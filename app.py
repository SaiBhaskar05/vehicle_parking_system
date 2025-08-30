from flask import Flask
from models.user import db
from controllers.login import login_bp
from controllers.signup import signup_bp
from controllers.add_lots import addlots_bp
from controllers.logout import logout_bp
from controllers.admin import admin_bp
from controllers.edit_lot import editlots_bp
from controllers.user import user_bp
from controllers.booking import booking_bp


app = Flask(__name__)
app.secret_key = 'saibhaskarnanduri'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle.db'

db.init_app(app)

with app.app_context(): 
    db.create_all()


app.register_blueprint(login_bp, url_prefix='/')

app.register_blueprint(signup_bp, url_prefix='/signup/')

app.register_blueprint(admin_bp, url_prefix='/admin/')

app.register_blueprint(addlots_bp, url_prefix='/addlot/')

app.register_blueprint(editlots_bp, url_prefix='/editlot/')

app.register_blueprint(logout_bp, url_prefix='/logout/')

app.register_blueprint(user_bp, url_prefix='/user')

app.register_blueprint(booking_bp, url_prefix='/booking')

if __name__=='__main__':
    app.run(debug=True)