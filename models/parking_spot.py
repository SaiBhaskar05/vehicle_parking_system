from . import db

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
