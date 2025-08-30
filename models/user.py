from . import db

class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable= True)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    pincode=db.Column(db.String(10), nullable=False)
    