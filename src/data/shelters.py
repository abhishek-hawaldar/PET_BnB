import datetime
import mongoengine

from data.bookings import Booking


class Shelter(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_meters = mongoengine.FloatField(required=True)
    is_carpeted = mongoengine.BooleanField(required=True)
    has_toys = mongoengine.BooleanField(required=True)
    allow_dangerous_pets = mongoengine.BooleanField(default=False)


    meta = {
        'db_alias': 'core',
        'collection': 'shelters'
    }
