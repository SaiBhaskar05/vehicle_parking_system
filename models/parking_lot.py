from . import db

class ParkingLot(db.Model):
    lot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    primelocation = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)