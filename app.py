# app.py

from flask import Flask, request, jsonify, Response
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import json


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies = movies_schema.dump(Movie.query.all())
        result = []
        for movie in movies:
            dict = {
                'id': movie['id'],
                'title': movie['title'],
                'description': movie['description'],
                'trailer': movie['trailer'],
                'year': movie['year'],
                'rating': movie['rating'],
                'genre_id': movie['genre_id'],
                'director_id': movie['director_id']
                }
            result.append(dict)
        return result, 200


@movie_ns.route('/<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        movie = movie_schema.dump(Movie.query.get(mid))
        result = {
            'id': movie['id'],
            'title': movie['title'],
            'description': movie['description'],
            'trailer': movie['trailer'],
            'year': movie['year'],
            'rating': movie['rating'],
            'genre_id': movie['genre_id'],
            'director_id': movie['director_id']
        }
        return result, 200


if __name__ == '__main__':
    # client = app.test_client()
    # response = client.get('/movies/')
    app.run(debug=True)
