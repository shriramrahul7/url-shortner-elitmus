import string
import random
from app import db
def shorten_url(long : str, host_len : int)->str:
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    short = ''.join(random.choices(letters, k=20-host_len))
    return short

class Urls(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(20))
    visits = db.Column("visits", db.Integer)

    def __init__(self, long, short):
        self.long = long
        self.short = short
        self.visits = 0