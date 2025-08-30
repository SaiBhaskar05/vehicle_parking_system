from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from datetime import datetime, timezone
from math import ceil
from zoneinfo import ZoneInfo

from models.parking_lot import ParkingLot, db
from models.parking_spot import ParkingSpot
from models.user import User
from models.book import Booking, current_utc_time

booking_bp = Blueprint('booking', __name__)
IST_ZONE = ZoneInfo("Asia/Kolkata")


@booking_bp.route('/book/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    username = session.get('user_username')

    if not username:
        flash("Please log in first.", "error")
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        spot_id = request.form.get('spot_id')
        vehicle_number = request.form.get('vehicle_number')

        if not spot_id or not vehicle_number:
            flash("All fields are required.", "error")
            return redirect(request.url)

        spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot.lot_id, status=False).first()
        if not spot:
            flash("Sorry, the selected spot is no longer available.", "error")
            return redirect(url_for('user.dashboard'))

        spot.status = True

        new_booking = Booking(
            username=username,
            lot_id=lot.lot_id,
            spot_id=spot.id,
            starttime=current_utc_time(),
            vehicle_number=vehicle_number
        )
        db.session.add(new_booking)
        db.session.commit()

        flash("Parking spot successfully booked!", "success")
        return redirect(url_for('user.dashboard'))

    spot = ParkingSpot.query.filter_by(lot_id=lot.lot_id, status=False).first()
    if not spot:
        flash("No available spots at this lot.", "error")
        return redirect(url_for('user.dashboard'))

    return render_template('booking.html', lot=lot, spot=spot, user=username)


@booking_bp.route('/booking_details/<int:lotid>/<int:spot_id>', methods=['GET'])
def booking_details(lotid, spot_id):
    lot = ParkingLot.query.get(lotid)
    spot = ParkingSpot.query.get(spot_id)
    booking = Booking.query.filter_by(lot_id=lotid, spot_id=spot_id).first()

    if not booking:
        flash("No booking found for this spot.", "error")
        return redirect(url_for('user.dashboard'))

    return render_template('occupieddetails.html', lot=lot, spot=spot, booking=booking)

@booking_bp.route('/release/<int:booking_id>', methods=['GET', 'POST'])
def release_spot(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    spot = ParkingSpot.query.get_or_404(booking.spot_id)
    current_time = datetime.now(timezone.utc)

    RATE_PER_HOUR = int(booking.lot.price)

    start_utc = booking.starttime
    if start_utc.tzinfo is None:
        start_utc = start_utc.replace(tzinfo=timezone.utc)

    if booking.endtime:
        end_utc = booking.endtime
    else:
        end_utc = current_time

    if end_utc.tzinfo is None:
        end_utc = end_utc.replace(tzinfo=timezone.utc)

    duration_seconds = (end_utc - start_utc).total_seconds()
    duration_hours = max(1, ceil(duration_seconds / 3600))
    calculated_price = duration_hours * RATE_PER_HOUR

    if request.method == 'POST':
        if not booking.endtime:
            booking.endtime = current_time
        if booking.prize is None:
            booking.prize = calculated_price
        spot.status = False
        db.session.commit()
        flash(f"Spot released successfully! Total charge: ₹{booking.prize}", "success")
        return redirect(url_for('user.dashboard'))

    return render_template(
        'release.html',
        booking=booking,
        current_time=current_time,
        duration_hours=duration_hours,
        calculated_price=calculated_price,
        zoneinfo=IST_ZONE
    )
