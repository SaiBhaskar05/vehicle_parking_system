from flask import Blueprint, url_for,render_template,redirect, request, flash
from models.user import User, db

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']
       fullname = request.form['fullname']
       address = request.form['address']
       age = request.form['userage']
       pincode = request.form['pincode']

       existinguser = User.query.filter((User.email == email)|(User.username == username)).first()
       if existinguser:
           flash("User already exist")
           return redirect(url_for('signup.signup'))
       newuser = User(username=username, email=email, password=password, fullname=fullname,age=age, address=address,pincode=pincode)
       db.session.add(newuser)
       db.session.commit()
       return redirect(url_for('login.login'))
    return render_template('signup.html')