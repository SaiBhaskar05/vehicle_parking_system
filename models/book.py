from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from . import db

def current_utc_time():
    return datetime.now(timezone.utc)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id', ondelete='RESTRICT'), nullable=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete='RESTRICT'), nullable=True)
    starttime = db.Column(db.DateTime, default=current_utc_time)
    endtime = db.Column(db.DateTime, nullable=True)
    vehicle_number = db.Column(db.String, nullable=False)
    prize = db.Column(db.Float, nullable=True)

    lot = db.relationship('ParkingLot', backref='bookings')
    spot = db.relationship('ParkingSpot', backref='bookings')
    user = db.relationship('User', backref='bookings')

    @property
    def starttime_ist(self):
        if not self.starttime:
            return None
        utc_dt = self.starttime
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(ZoneInfo("Asia/Kolkata"))

    @property
    def endtime_ist(self):
        if not self.endtime:
            return None
        utc_dt = self.endtime
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(ZoneInfo("Asia/Kolkata"))
    
    @property
    def is_released(self):
        return self.endtime is not None

