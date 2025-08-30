from flask import Blueprint, url_for, render_template, redirect, request, flash
from models.parking_lot import ParkingLot, db
from models.parking_spot import ParkingSpot
from models.book import Booking

editlots_bp = Blueprint('edit_lot', __name__)

@editlots_bp.route('/edit/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    occupied_spots = Booking.query.filter_by(lot_id=lot_id).count()

    if request.method == 'POST':
        try:
            new_max_spots = int(request.form['max_spots'])

            if new_max_spots < occupied_spots:
                flash(
                    f"Cannot reduce max spots to {new_max_spots}: "
                    f"{occupied_spots} spot(s) are already booked.",
                    "danger"
                )
                return redirect(request.url)

            old_max_spots = lot.max_spots

            lot.primelocation = request.form['primelocation']
            lot.address = request.form['address']
            lot.pincode = request.form['pincode']
            lot.price = request.form['price']
            lot.max_spots = new_max_spots

            if new_max_spots > old_max_spots:
               
                extra_count = new_max_spots - old_max_spots
                for _ in range(extra_count):
                    new_spot = ParkingSpot(lot_id=lot.lot_id)
                    db.session.add(new_spot)

            elif new_max_spots < old_max_spots:
                remove_count = old_max_spots - new_max_spots
                spots_to_remove = (ParkingSpot.query
                    .filter_by(lot_id=lot.lot_id)
                    .order_by(ParkingSpot.id.desc())
                    .limit(remove_count)
                    .all())
                for spot in spots_to_remove:
                    db.session.delete(spot)

            db.session.commit()
            flash("Parking lot updated successfully!", "success")
            return redirect(url_for('admin.dashboard'))

        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(f"Invalid form data: {e}", "danger")

    return render_template('editlot.html', lot=lot, occupied_spots=occupied_spots)
