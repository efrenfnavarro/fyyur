from app import db
import enum

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    shows = db.relationship('Show', backref=db.backref('venue', lazy=True), cascade="all, delete")

    def __repr__(self):
          return '<Venue {}>'.format(self.name)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    shows = db.relationship('Show', backref=db.backref('artist', lazy=True), cascade="all, delete")

    def __repr__(self):
          return '<Artist {}>'.format(self.name)

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'),
        nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
        nullable=False)
    starttime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
          return '<Show {}{}'.format(self.artist_id, self.venue_id)
