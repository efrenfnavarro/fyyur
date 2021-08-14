#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------
#----------------------------------------------------------------------------#
#  Venues - LIST
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():

  areas = Venue.query.distinct('city','state').all()
  data = []

  for area in areas:
        area_venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
        venue_data = []

        for venue in area_venues:
              record={
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.starttime > datetime.now()).all())
              } 
              venue_data.append(record)

        data.append({
          "city": area.city,
          "state": area.state,
          "venues": venue_data
        })

  return render_template('pages/venues.html', areas=data);

#----------------------------------------------------------------------------#
#  Venues - search
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term','')
  search_results = db.session.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()

  data = []

  for search in search_results:
        record ={
          "id": search.id,
          "name": search.name,
          "num_upcomig_shows": len(db.session.query(Show).filter(Show.venue_id == Venue.id).filter(Show.starttime > datetime.now()).all())
        }
        data.append(record)
  
  response={
    "count": len(search_results),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#----------------------------------------------------------------------------#
#  Venues - show_venue(venue_id)
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  if not venue:
      return render_template('errors/404.html'), 404

  past_shows = []
  upcoming_shows = []

  past_shows_results = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.starttime < datetime.now()).all()
  for show in past_shows_results:
        record = {
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.starttime.strftime('%Y-%m-%d %H:%M:%S')
        }
        past_shows.append(record)

  upcoming_shows_results = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.starttime > datetime.now()).all()
  for show in upcoming_shows_results:
        record = {
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.starttime.strftime('%Y-%m-%d %H:%M:%S')
        }
        upcoming_shows.append(record)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),   
  }
  
  return render_template('pages/show_venue.html', venue=data)

#-----------------------------------------------------------------
#  Create Venue
# ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  
  try:
    seeking_talent = False 
    if 'seeking_talent' in request.form:
      seeking_talent = request.form['seeking_talent'] == 'y'
    venue = Venue(
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      address = request.form['address'],
      city = request.form['city'],
      state = request.form['state'],      
      phone = request.form['phone'],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website = request.form['website_link'],
      seeking_talent = seeking_talent,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info()) 
  finally:
    db.session.close()
    
  if error:
    flash(f'An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash(f'Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues - DELETE
#----------------------------------------------------------------
#@app.route('/venues/<venue_id>', methods=['DELETE'])
#@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  venue = Venue.query.get(venue_id)

  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
      flash(f'Error while trying to delete venue { venue.name }. Please Try again.')
  else:
      flash(f'The Venue { venue.name } was successfully deleted.')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#------------------------------------------------------------------
#  Artists - LIST
#------------------------------------------------------------------
@app.route('/artists')
def artists():
  
  artists = Artist.query.all()
  data = []

  for artist in artists:
    record={
      'id': artist.id,
      'name': artist.name
    } 
    data.append(record)

  return render_template('pages/artists.html', artists=data)


#------------------------------------------------------------------
#  Artists - SEARCH
#------------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term','')
  search_results = db.session.query(Artist).filter(Artist.name.ilike(f"%{search_term}%")).all()

  data = []

  for search in search_results:
        record ={
          "id": search.id,
          "name": search.name,
          "num_upcomig_shows": len(db.session.query(Show).filter(Show.artist_id == Artist.id).filter(Show.starttime > datetime.now()).all())
        }
        data.append(record)
  
  response={
    "count": len(search_results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#------------------------------------------------------------------
#  Artists - GET(artist_id)
#------------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  if not artist:
    return render_template('errors/404.html'), 404

  past_shows= []
  upcoming_shows = []

  past_shows_results = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.starttime < datetime.now()).all()
  for show in past_shows_results:
        record = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.starttime.strftime('%Y-%m-%d %H:%M:%S')
        }
        past_shows.append(record)

  upcoming_shows_results = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.starttime > datetime.now()).all()
  for show in upcoming_shows_results:
        record = {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time":  show.starttime.strftime('%Y-%m-%d %H:%M:%S')
        }
        upcoming_shows.append(record)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#------------------------------------------------------------------
#  Artists - UPDATE
#------------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist:
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue =True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash(f'An error occured, Artist { artist_id } was not edited!')
  else:
    flash(f'Artist was updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

#------------------------------------------------------------------
#  Venues - EDIT(venue_id)
#------------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  venue = Venue.query.get(venue_id)

  try:
      venue.name = request.form['name']
      venue.genres = request.form.getlist('genres') 
      venue.address = request.form['address']  
      venue.city = request.form['city'] 
      venue.state = request.form['state'] 
      venue.phone = request.form['phone'] 
      venue.website = request.form['website_link'] 
      venue.facebook_link = request.form['facebook_link'] 
      venue.seeking_talent = True if 'seeking_talent' in request.form else False 
      venue.seeking_description = request.form['seeking_description'] 
      venue.image_link = request.form['image_link']   
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
        flash(f'An error occurred. Venue could not be changed.')
  else:
        flash(f'Venue was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#------------------------------------------------------------------
#  Create Artist
#------------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False

  try:
    seeking_venue1 = False
    if 'seeking_venue' in request.form:
      seeking_venue1 = request.form['seeking_venue'] == 'y'
    artist = Artist(
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website = request.form['website_link'],
      seeking_venue = seeking_venue1,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
  except :
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
      flash(f'An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
      flash(f'Artist ' + request.form['name'] + ' was successfully listed!')
    
  return render_template('pages/home.html')

#------------------------------------------------------------------
#  Artist - DELETE
#------------------------------------------------------------------
@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  artist = Artist.query.get(artist_id)

  try:
    db.session.delete(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()

  if error:
      flash(f'Error while trying to delete Artist { artist.name }. Please Try again.')
  else:
      flash(f'The Artist { artist.name } was successfully deleted.')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#------------------------------------------------------------------
#  Shows - LIST
#------------------------------------------------------------------
@app.route('/shows')
def shows():

  shows = Show.query.order_by(Show.starttime.desc()).all()
  data = []

  for show in shows:
      artist = db.session.query(Artist).filter_by(id = show.artist_id).first_or_404()
      venue = db.session.query(Venue).filter_by(id =show.venue_id).first_or_404()

      record={
        'venue_id': venue.id,
        'venue_name': venue.name,
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.starttime.strftime("%m/%d/%Y, %H:%M")
      } 
      data.append(record)

  return render_template('pages/shows.html', shows=data)

#------------------------------------------------------------------
#  Shows - CREATE
#------------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  try:
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      starttime = request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys._exc_info())
  finally:
      db.session.close()

  if error:
      flash(f'An error occurred. Show could not be listed.')
  else:
      flash(f'Show was successfully listed!')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
