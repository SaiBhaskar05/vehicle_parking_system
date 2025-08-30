from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.user import User, db
from models.book import Booking

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def dashboard():
    parking_lots = ParkingLot.query.all()
    lot_spots_map = {}
    for lot in parking_lots:
        lot_spots_map[lot.lot_id] = lot.spots
    return render_template('admin.html', parking_lots=parking_lots, lot_spots_map=lot_spots_map)

@admin_bp.route('/userreg')
def userreg():
    users = User.query.offset(1).all()
    return render_template('usersreg.html', users=users)


@admin_bp.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    users = User.query.first()
    if request.method == 'POST':
        users.username = request.form['username']
        users.fullname = request.form['fullname']
        users.email = request.form['email']
        users.address = request.form['address']
        users.pincode = request.form['pincode']
        users.password = request.form['password']
        flash("Successfully Edited")
        db.session.commit()
    return render_template('admineditprofile.html', users=users)

@admin_bp.route('/deletelot/<int:lot_id>', methods=['GET','POST'])
def deletelot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupiedspot = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status=True).first()
    if occupiedspot:
        flash("Cannot delete lot with occupied parking spots!", "error")
        return redirect(url_for('admin.dashboard'))

    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()

    flash("Parking lot deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/summary', methods=['GET'])
def summary():
    all_bookings = Booking.query.all()

    rows = []
    for b in all_bookings:
        if b.starttime_ist and b.lot:
            duration = None
            if b.endtime_ist:
                duration = (b.endtime_ist - b.starttime_ist).total_seconds() / 3600
            rows.append({
                'starttime': b.starttime_ist,
                'prize': b.prize,
                'primelocation': b.lot.primelocation,
                'duration': duration
            })

    df = pd.DataFrame(rows)

    plot_url1 = None
    plot_url2 = None
    plot_url3 = None

    if not df.empty:
        df['month'] = df['starttime'].dt.to_period('M')
        monthly_revenue = df.groupby('month')['prize'].sum()

        fig1, ax1 = plt.subplots(figsize=(8, 5))
        monthly_revenue.plot(kind='line', marker='o', color='green', ax=ax1)
        ax1.set_title('Total Revenue Over Time')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Revenue (₹)')
        plt.xticks(rotation=45)
        fig1.tight_layout()

        img1 = io.BytesIO()
        fig1.savefig(img1, format='png')
        img1.seek(0)
        plot_url1 = base64.b64encode(img1.getvalue()).decode()
        plt.close(fig1)

        lot_counts = df['primelocation'].value_counts()

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        lot_counts.plot(kind='bar', color='orange', ax=ax2)
        ax2.set_title('Most Popular Parking Lots')
        ax2.set_xlabel('Prime Location')
        ax2.set_ylabel('Number of Bookings')
        fig2.tight_layout()

        # Add count labels
        max_count = lot_counts.max()
        ax2.set_ylim(0, max_count * 1.2)
        for i, v in enumerate(lot_counts):
            ax2.text(i, v + max_count * 0.02, str(v), ha='center', va='bottom', fontsize=9)

        img2 = io.BytesIO()
        fig2.savefig(img2, format='png')
        img2.seek(0)
        plot_url2 = base64.b64encode(img2.getvalue()).decode()
        plt.close(fig2)

        df_duration = df.dropna(subset=['duration'])
        if not df_duration.empty:
            avg_duration = df_duration.groupby('month')['duration'].mean()

            fig3, ax3 = plt.subplots(figsize=(8, 5))
            avg_duration.plot(kind='line', marker='o', color='blue', ax=ax3)
            ax3.set_title('Average Booking Duration Over Time')
            ax3.set_xlabel('Month')
            ax3.set_ylabel('Avg Duration (Hours)')
            plt.xticks(rotation=45)
            fig3.tight_layout()

            img3 = io.BytesIO()
            fig3.savefig(img3, format='png')
            img3.seek(0)
            plot_url3 = base64.b64encode(img3.getvalue()).decode()
            plt.close(fig3)

    return render_template(
        'adminsummary.html',
        plot_url1=plot_url1,
        plot_url2=plot_url2,
        plot_url3=plot_url3
    )
