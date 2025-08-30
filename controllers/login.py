from flask import Blueprint, url_for, flash, render_template, request, session, redirect
from models.user import User

login_bp = Blueprint('login', __name__)

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        loguser = User.query.filter_by(email=email, password=password).first()

        if loguser:
            session['user_username'] = loguser.username
            session['user_email'] = loguser.email
            session['user_fullname'] = loguser.fullname

            if loguser.email == 'saibhaskarnanduri1@gmail.com':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid Credentials')
            return redirect(url_for('login.login'))
    
    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login.login'))
