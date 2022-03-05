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
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        # movies = Movie.query.all()
        # result = []
        # for movie in movies:
        #     dict = {
        #         'id': movie.id,
        #         'title': movie.title,
        #         'description': movie.description,
        #         'trailer': movie.trailer,
        #         'year': movie.year,
        #         'rating': movie.rating,
        #         'genre_id': Genre.query.get(movie.genre_id).name,
        #         'director_id': Director.query.get(movie.director_id).name
        #         }
        #     result.append(dict)
        # return result, 200
        movies = movies_schema.dump(Movie.query.all())
        # result = []
        # for movie in movies:
        #     dict = {
        #         'id': movie['id'],
        #         'title': movie['title'],
        #         'description': movie['description'],
        #         'trailer': movie['trailer'],
        #         'year': movie['year'],
        #         'rating': movie['rating'],
        #         'genre_id': movie['genre_id'],
        #         'director_id': movie['director_id']
        #         }
        #     result.append(dict)

        dir_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        find = False

        if dir_id or genre_id:
            for movie in movies:
                if dir_id and genre_id:
                    if dir_id == str(movie['director_id']) and genre_id == str(movie['genre_id']):
                        find = True
                        return movie, 200
                elif dir_id:
                    if dir_id == str(movie['director_id']):
                        find = True
                        return movie, 200
                elif genre_id:
                    if genre_id == str(movie['genre_id']):
                        find = True
                        return movie, 200
                # if not find:
                #     return '', 404

        return movies, 200


@movie_ns.route('/<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        movie = movie_schema.dump(Movie.query.get(mid))
        # result = {
        #     'id': movie['id'],
        #     'title': movie['title'],
        #     'description': movie['description'],
        #     'trailer': movie['trailer'],
        #     'year': movie['year'],
        #     'rating': movie['rating'],
        #     'genre_id': movie['genre_id'],
        #     'director_id': movie['director_id']
        # }
        return movie, 200


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def put(self, did):
        req_json = request.json
        director = Director.query.get(did)
        director.name = req_json["name"]
        db.session.add(director)
        db.session.commit()
        db.session.close()
        return '', 201

    def delete(self, did):
        director = Director.query.get(did)
        db.session.delete(director)
        db.session.commit()
        db.session.close()
        return '', 204


@genre_ns.route('/')
class GenresView(Resource):
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def put(self, gid):
        req_json = request.json
        genre = Genre.query.get(gid)
        genre.name = req_json["name"]
        db.session.add(genre)
        db.session.commit()
        db.session.close()
        return '', 201

    def delete(self, gid):
        genre = Genre.query.get(gid)
        db.session.delete(genre)
        db.session.commit()
        db.session.close()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
