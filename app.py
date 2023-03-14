from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class MusicLibrary(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)
    artist = db.Column(db.String(255), nullable = False)
    album = db.Column(db.String(255), nullable = False)
    release_date = db.Column(db.Date)
    genre = db.Column(db.String(255))

    def __repr__(self):
        return f'{self.title} {self.artist} {self.album} {self.release_date} {self.genre}'

# Schemas
class SongSchema(ma.Schema):
    id = fields.Integer(primary_key = True)
    title = fields.String(required = True)
    artist = fields.String(required = True)
    album = fields.String(required = True)
    release_date = fields.Date()
    genre = fields.String()

    class Meta:
        fields = ("id", "title", "artist", "album", "release_date", "genre")

    @post_load
    def create_song(self, data, **kwargs):
        return MusicLibrary(**data)

song_schema = SongSchema()
songs_schema = SongSchema(many = True)

# Resources

class SongListResource(Resource):
    def get(self):
        all_songs = MusicLibrary.query.all()
        return song_schema.dump(all_songs), 200
    
    def post(self):
        form_data = request.get_json()
        try:
            new_song = song_schema.load(form_data)
            db.session.add(new_song)

# Routes
