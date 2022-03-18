from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, }
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


class FilterSchema(Schema):
    director_id = fields.Int(required=False)
    genre_id = fields.Int(required=False)


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        filtered_data = FilterSchema().load(request.args)
        movies = Movie.query.filter_by(**filtered_data).all()
        return MovieSchema(many=True).dump(movies), 200


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = movie_schema.dump(Movie.query.get(mid))
        if movie == {}:
            return "Not found", 404
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
        if director is None:
            return "Not found", 404
        director.name = req_json["name"]
        db.session.add(director)
        db.session.commit()
        db.session.close()
        print(director)
        return '', 201

    def delete(self, did):

        director = Director.query.get(did)
        if director is None:
            return "Not found", 404
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
        if genre is None:
            return "Not found", 404
        genre.name = req_json["name"]
        db.session.add(genre)
        db.session.commit()
        db.session.close()
        return '', 201

    def delete(self, gid):

        genre = Genre.query.get(gid)
        if genre is None:
            return "Not found", 404
        db.session.delete(genre)
        db.session.commit()
        db.session.close()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
