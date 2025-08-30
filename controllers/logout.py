from flask import Blueprint, url_for, flash, render_template, request, session, redirect
from models.user import User

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login.login'))