from flask import Blueprint, url_for, render_template, redirect, request, flash
from models.parking_lot import ParkingLot, db
from models.parking_spot import ParkingSpot

addlots_bp = Blueprint('add_lots', __name__)

@addlots_bp.route('/', methods=['GET', 'POST'])
def add_lots():
    if request.method == 'POST':
        primelocation = request.form['primelocation']
        address = request.form['address']
        pincode = request.form['pincode']
        price = request.form['price']
        max_spots = int(request.form['max_spots'])

        new_lot = ParkingLot(
            primelocation=primelocation,
            address=address,
            pincode=pincode,
            price=price,
            max_spots=max_spots
        )
        db.session.add(new_lot)
        db.session.commit()
        
        spots = [
            ParkingSpot(lot_id=new_lot.lot_id)
            for _ in range(max_spots)
        ]
        db.session.add_all(spots)
        db.session.commit()

        flash("Parking lot and spots added successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('addlot.html')
