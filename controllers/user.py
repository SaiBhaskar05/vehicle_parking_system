from flask import Blueprint, session, request, render_template, redirect, flash, url_for
from models.user import User, db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.book import Booking

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd

import io
import base64

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'user_fullname' not in session or 'user_username' not in session:
        return redirect('/')

    search_input = None
    parking_lots = ParkingLot.query.all()

    if request.method == 'POST':
        search_input = request.form.get('search_term', '').strip()
        if search_input:
            parking_lots = ParkingLot.query.filter(
                (ParkingLot.pincode == search_input) | 
                (ParkingLot.primelocation.ilike(f"%{search_input}%"))
            ).all()
        else:
            flash("Please enter a valid search term.", "warning")
   
    lot_availability = {}
    for lot in parking_lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status=False).count()
        lot_availability[lot.lot_id] = "Available" if available_spots > 0 else "Not Available"


    recent_bookings = Booking.query.filter_by(username=session['user_username'])\
                                   .order_by(Booking.starttime.desc())\
                                   .limit(5).all()

    return render_template(
        'user.html',
        fullname=session['user_fullname'],
        parking_lots=parking_lots,
        input=search_input,
        lot_availability=lot_availability,
        recent_bookings=recent_bookings
    )

@user_bp.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    if 'user_username' not in session:
        return redirect('/')

    user = User.query.get(session['user_username'])

    if not user:
        flash("User not found.", "error")
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        user.username = request.form['username']
        user.fullname = request.form['fullname']
        user.email = request.form['email']
        user.address = request.form['address']
        user.pincode = request.form['pincode']
        user.password = request.form['password']
        flash("Profile updated successfully!", "success")
        db.session.commit()
        session['user_fullname'] = user.fullname

    return render_template('usereditprofile.html', user=user, fullname=session['user_fullname'])

@user_bp.route('/summary', methods=['GET'])
def summary():
    if 'user_fullname' not in session or 'user_username' not in session:
        return redirect('/')

    all_bookings = Booking.query.filter_by(username=session['user_username']).all()

    rows = []
    for b in all_bookings:
        if b.starttime_ist and b.lot:
            rows.append({
                'primelocation': b.lot.primelocation,
                'prize': b.prize
            })

    df = pd.DataFrame(rows)

    plot_url1 = None
    plot_url2 = None
    total_spent = 0

    if not df.empty:
        total_spent = df['prize'].sum()

        location_spend = df.groupby('primelocation')['prize'].sum().sort_values(ascending=False)

        fig1, ax1 = plt.subplots()
        location_spend.plot(kind='bar', ax=ax1, color='green')
        ax1.set_title('Total Cost Spent in Each Parking Lot')
        ax1.set_xlabel('Prime Location')
        ax1.set_ylabel('Total Amount Spent (₹)')
        ax1.set_ylim(0, 300)
        fig1.tight_layout()

        for i, v in enumerate(location_spend):
            ax1.text(i, v + 5, f'₹{v:.0f}', ha='center', va='bottom', fontsize=9)

        img1 = io.BytesIO()
        fig1.savefig(img1, format='png')
        img1.seek(0)
        plot_url1 = base64.b64encode(img1.getvalue()).decode()
        plt.close(fig1)

        location_counts = df['primelocation'].value_counts()

        fig2, ax2 = plt.subplots()
        location_counts.plot(kind='bar', ax=ax2, color='orange')
        ax2.set_title('Your Parking Lot Preferences')
        ax2.set_xlabel('Prime Location')
        ax2.set_ylabel('Number of Bookings')
        ax2.set_ylim(0, 10)
        fig2.tight_layout()

        for i, v in enumerate(location_counts):
            ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=9)

        img2 = io.BytesIO()
        fig2.savefig(img2, format='png')
        img2.seek(0)
        plot_url2 = base64.b64encode(img2.getvalue()).decode()
        plt.close(fig2)

    return render_template(
        'usersummary.html',
        fullname=session['user_fullname'],
        plot_url1=plot_url1,
        plot_url2=plot_url2,
        total_spent=total_spent
    )
